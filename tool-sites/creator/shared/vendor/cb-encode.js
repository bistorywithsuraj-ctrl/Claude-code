/* Creator Bench frame-accurate video export.
   Draws every frame with drawFrame(t), encodes it with WebCodecs and muxes an MP4 (mp4-muxer, MIT).
   No frames are dropped at any resolution. Optional mono audio track (Float32Array PCM).
   Usage: await CBEncode.render({ canvas, width, height, fps, duration, drawFrame, audio, sampleRate, onProgress }) -> Blob */
(function () {
  const supported = () => typeof window.VideoEncoder === 'function' && typeof window.VideoFrame === 'function' && typeof window.Mp4Muxer === 'object';
  async function pickVideo(width, height, fps, bitrate) {
    const tries = [
      ['avc', 'avc1.640034'], ['avc', 'avc1.640033'], ['avc', 'avc1.64002A'], ['avc', 'avc1.640028'], ['avc', 'avc1.4D0033'], ['avc', 'avc1.42003E'],
      ['vp9', 'vp09.00.51.08'], ['vp9', 'vp09.00.41.08'],
    ];
    for (const [kind, codec] of tries) {
      for (const hardwareAcceleration of ['prefer-hardware', 'no-preference', 'prefer-software']) {
        const cfg = { codec, width, height, bitrate, framerate: fps, hardwareAcceleration, latencyMode: 'quality' };
        try { const r = await VideoEncoder.isConfigSupported(cfg); if (r.supported) return { kind, cfg: r.config || cfg }; } catch (e) {}
      }
    }
    return null;
  }
  async function pickAudio(sampleRate) {
    if (typeof window.AudioEncoder !== 'function') return null;
    for (const [mux, codec] of [['aac', 'mp4a.40.2'], ['opus', 'opus']]) {   // AAC first; Opus where AAC isn't licensed
      const cfg = { codec, sampleRate, numberOfChannels: 1, bitrate: 128000 };
      try { const r = await AudioEncoder.isConfigSupported(cfg); if (r.supported) return { mux, cfg }; } catch (e) {}
    }
    return null;
  }
  async function render(o) {
    const { canvas, width, height, fps = 30, duration, drawFrame, onProgress = () => {} } = o;
    const bitrate = o.bitrate || Math.round(width * height * fps * 0.12);
    const v = await pickVideo(width, height, fps, bitrate);
    if (!v) throw new Error(`This browser can't encode ${width}×${height}. Try a smaller resolution.`);
    const sampleRate = o.sampleRate || 48000, acfg = o.audio ? await pickAudio(sampleRate) : null;
    const muxer = new Mp4Muxer.Muxer({ target: new Mp4Muxer.ArrayBufferTarget(), fastStart: 'in-memory', firstTimestampBehavior: 'offset',
      video: { codec: v.kind, width, height, frameRate: fps }, audio: acfg ? { codec: acfg.mux, numberOfChannels: 1, sampleRate } : undefined });
    let failure = null;
    const ve = new VideoEncoder({ output: (chunk, meta) => muxer.addVideoChunk(chunk, meta), error: e => { failure = e; } });
    ve.configure(v.cfg);
    const total = Math.max(1, Math.round(duration * fps)), us = 1e6 / fps;
    for (let f = 0; f < total; f++) {
      if (failure) throw failure;
      await drawFrame(f / fps);
      const frame = new VideoFrame(canvas, { timestamp: Math.round(f * us), duration: Math.round(us) });
      ve.encode(frame, { keyFrame: f % (fps * 2) === 0 }); frame.close();
      while (ve.encodeQueueSize > 4) await new Promise(r => setTimeout(r, 4));
      if (f % 3 === 0) { onProgress(f / total * (acfg ? .95 : 1)); await new Promise(r => setTimeout(r, 0)); }
    }
    await ve.flush(); ve.close(); if (failure) throw failure;
    if (acfg) {
      const ae = new AudioEncoder({ output: (chunk, meta) => muxer.addAudioChunk(chunk, meta), error: e => { failure = e; } });
      ae.configure(acfg.cfg); const pcm = o.audio, step = 1024 * 8;
      for (let i = 0; i < pcm.length; i += step) {
        const part = pcm.subarray(i, Math.min(pcm.length, i + step));
        const ad = new AudioData({ format: 'f32-planar', sampleRate, numberOfFrames: part.length, numberOfChannels: 1, timestamp: Math.round(i / sampleRate * 1e6), data: part });
        ae.encode(ad); ad.close();
      }
      await ae.flush(); ae.close(); if (failure) throw failure;
    }
    muxer.finalize(); onProgress(1);
    return { blob: new Blob([muxer.target.buffer], { type: 'video/mp4' }), codec: v.kind, audio: !!acfg };
  }
  window.CBEncode = { supported, render };
})();
