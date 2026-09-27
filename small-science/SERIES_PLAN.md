# SMALL SCIENCE: the hidden science of F1, football and AI
**Format:** 60–90 s Shorts and 6–10 min long-form, both rendered from the same code
**Look:** paper-cutout world · light-gray paper · yellow highlighter · green cards · stop-motion "boil"
**Host:** Pip, an original paper-cutout kid scientist (green coat, round glasses)
**Engine:** `lib/paper.js` + `lib/characters.js`. Each episode is one HTML file and renders with `render.py`.
**Voice:** your Mac voice model (one WAV per caption line) or Fish Audio free tier

> Every number gets checked before narration is recorded. Lines marked **[VERIFY]** change with the rules or come from press reports.

---

## 🏎️ FORMULA 1
| # | Episode | Hook | Science beats |
|---|---|---|---|
| F1-1 | **300 km, one tank** ✅ *built* | Why F1 cars never refuel | refuelling ban 2010 · 110 kg max race fuel (2022–25) [VERIFY 2026 rules] · ~2 km/L · >50 % thermal efficiency · ~0.03 s/lap per kg |
| F1-2 | **Why F1 cars could drive upside down** | More downforce than their own weight | wings as upside-down aeroplane wings · ground effect · downforce grows with speed² · the "ceiling" speed estimate [VERIFY] |
| F1-3 | **Why tyres are bald** | No tread on a dry track | contact patch · slick vs grooved · tyre temperature window · why rain tyres throw out water [VERIFY litres/s] |
| F1-4 | **How brakes glow at 1000 °C** | Carbon discs turning orange | kinetic energy → heat · carbon-carbon discs · ~5 g deceleration · energy recovery (MGU-K) |
| F1-5 | **How a 2-second pit stop works** | 20+ people, 2 seconds | choreography · wheel-gun torque · jacks · reaction time vs human limits |
| F1-6 | **Why drivers lose kilos in a race** | Sweat, heat, G-force | cockpit heat · fluid loss [VERIFY range] · neck muscles vs 5–6 g |
| F1-7 | **What DRS actually does** | Push-button overtaking | drag vs downforce · flap opening · slipstream (tow) physics |

## ⚽ FOOTBALL
| # | Episode | Hook | Science beats |
|---|---|---|---|
| FB-1 | **Why a football curves** (next) | The banana free kick | Magnus effect · spin → pressure difference · sidespin vs topspin |
| FB-2 | **The knuckleball** | A ball that wobbles with no spin | no spin → unstable airflow · drag crisis · panel seams |
| FB-3 | **Why a penalty is almost unsaveable** | 11 m, less than half a second | ball speed ÷ distance vs human reaction time · keeper guesses early |
| FB-4 | **How VAR offside lines are drawn** | Millimetre decisions | camera frame rates · the "kick point" problem · limbs & 3D models [VERIFY current tech] |
| FB-5 | **Why grass is cut in stripes** | Pitch patterns | light reflecting off bent blades · mowing direction, no paint |
| FB-6 | **Inside a football** | Why modern balls fly differently | panel count & seams · air pressure rules [VERIFY] · bladder |

## 🤖 AI
| # | Episode | Hook | Science beats |
|---|---|---|---|
| AI-1 | **How your phone unlocks with your face** | It "sees" you in the dark | infrared dot projector · depth map · matching on-device |
| AI-2 | **How autocorrect guesses your next word** | It knows what you'll type | predicting the next word from probabilities · a simple chain → large language models |
| AI-3 | **How a chatbot "reads"** | It doesn't read words | tokens · numbers as meaning (embeddings) · predicting the next token |
| AI-4 | **How spam filters catch scams** | Your inbox is guarded | patterns & features · learning from labelled examples |
| AI-5 | **How Maps knows about traffic** | The red line on the road | anonymous phone speeds · averaging · prediction |
| AI-6 | **How AI is used in F1 strategy** | Crossover episode | race simulations run thousands of times · tyre-wear models · probabilities of a safety car |

---

## Why this is hard to copy
1. **Same character, same world, every frame.** It's drawn in code, so there's no AI-image drift between shots. That makes the channel instantly recognisable.
2. **Accurate diagrams and numbers.** Molecules, forces and charts are computed from the numbers themselves, which AI-video channels can't match.
3. **One file per episode.** Scenes reuse the same parts (the car, the ball, Pip, cards, arrows), so each new episode is faster to make than the last.
4. **Shorts for free.** The same scenes can render vertically (9:16).
5. **Optional interactive page per episode** (e.g. "set the downforce and see if the car can drive upside down").
