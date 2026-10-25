# Speech quality details

Run `20261025-053632-9d5b8428` on NVIDIA GeForce RTX 5070 Ti.
Workload SHA-256: `6a968ddb530f978637db9ced405ab459fd3d437bdad8eb89caf9538d94958a46`. Reference SHA-256: `0a70c960986c7ddaad57a4fbd7c28209ab8911580f610f23d1363403346eb4d4`.
Fixed per-call seeds, concurrency one, explicit settings and discarded warmups. Checkpoints are never pooled.

## faster / 1.7B-CustomVoice / complete

Image `sha256:908f3bcb2be48436d1bdaf273085f759d170b62f98102e44a8b7a8bc51b05631`; source `36fa150a0cff236e299313ba0bbb80eff74ba2c7af7dfd90b2a706901056c29b`.
API ready 2.037s; cold load 14.681s; discarded warmups 1. Incremental waveform support: True.

Resident cohort: `1.7B-CustomVoice`.
Cold load and memory cover the listed resident set. The full product run retains each checkpoint through its applicable suites, then unloads it before the next.

| Group | Judged | Exact % | Mean similarity % | Minimum % | Errors |
|---|---|---|---|---|---|
| Mode: custom | 100 | 81.0 | 99.0 | 72.94 | 0 |
| Language: Chinese | 10 | 100.0 | 100.0 | 100.0 | 0 |
| Language: English | 10 | 100.0 | 100.0 | 100.0 | 0 |
| Language: French | 10 | 60.0 | 98.48 | 93.88 | 0 |
| Language: German | 10 | 40.0 | 94.05 | 72.94 | 0 |
| Language: Italian | 10 | 60.0 | 98.69 | 92.0 | 0 |
| Language: Japanese | 10 | 100.0 | 100.0 | 100.0 | 0 |
| Language: Korean | 10 | 100.0 | 100.0 | 100.0 | 0 |
| Language: Portuguese | 10 | 100.0 | 100.0 | 100.0 | 0 |
| Language: Russian | 10 | 80.0 | 99.4 | 95.05 | 0 |
| Language: Spanish | 10 | 70.0 | 99.37 | 97.67 | 0 |

### Hardest calls

| Call | Expected | Transcript | Similarity % |
|---|---|---|---|
| 1.7B-CustomVoice/german_custom_01_r4 | Der Morgenkaffee verhandelte hart, half dann aber doch. | Im Morgencafé verhandelte Hart auf Dunabador. | 72.94 |
| 1.7B-CustomVoice/german_custom_01_r5 | Der Morgenkaffee verhandelte hart, half dann aber doch. | Der Morgenkaffee verhandelte hart, hoffte aber doch. | 88.89 |
| 1.7B-CustomVoice/german_custom_01_r1 | Der Morgenkaffee verhandelte hart, half dann aber doch. | Der Morgenkaffee verhandelte ha, hofft dann aber doch | 90.11 |
| 1.7B-CustomVoice/italian_custom_02_r4 | Ho messo le chiavi in un posto sicuro, forse troppo sicuro. | Ho messo le chiavi in un posto sicuro, forse troppo con l'assicurò. | 92.0 |
| 1.7B-CustomVoice/german_custom_01_r2 | Der Morgenkaffee verhandelte hart, half dann aber doch. | Der Morgenkaffee verhandelte halt hofft dann aber doch. | 92.47 |
| 1.7B-CustomVoice/french_custom_01_r5 | Le café du matin a négocié ferme, puis il a accepté de m'aider. | Le café du matin a négocié fermes, puis il acceptait de m'aider. | 93.88 |
| 1.7B-CustomVoice/russian_custom_01_r3 | Утренний кофе долго торговался, но в итоге согласился помочь. | Утренникови долго торговался, но в итоге согласился помочь. | 95.05 |
| 1.7B-CustomVoice/french_custom_01_r3 | Le café du matin a négocié ferme, puis il a accepté de m'aider. | Le le café du matin a négocié ferme puis il a accepté de de m'aider | 96.0 |
| 1.7B-CustomVoice/french_custom_01_r4 | Le café du matin a négocié ferme, puis il a accepté de m'aider. | Le café du matin a négocié fermement puis il a accepté de m'aider. | 96.0 |
| 1.7B-CustomVoice/spanish_custom_01_r4 | El café de la mañana negoció duro, pero al final ayudó. | Eu café de la mañana negoció duro pero al final ayudó. | 97.67 |
| 1.7B-CustomVoice/italian_custom_01_r1 | Il caffè del mattino ha trattato duramente, ma poi ha aiutato. | Il caffè del mattino ha trattato duramente, ma poi aiutato. | 97.96 |
| 1.7B-CustomVoice/italian_custom_01_r2 | Il caffè del mattino ha trattato duramente, ma poi ha aiutato. | Il caffè del mattino ha trattato duramente ma poi aiutato. | 97.96 |
| 1.7B-CustomVoice/spanish_custom_02_r2 | Guardé las llaves en un lugar seguro, quizá demasiado seguro. | Guarda las llaves en un lugar seguro, quizá demasiado seguro. | 98.0 |
| 1.7B-CustomVoice/spanish_custom_02_r3 | Guardé las llaves en un lugar seguro, quizá demasiado seguro. | Guardelas llaves en un lugar seguro, quizá demasiado seguro. | 98.0 |
| 1.7B-CustomVoice/german_custom_02_r1 | Ich legte die Schlüssel an einen sicheren Ort, leider zu sicher. | Ich legte die Schlüssel an einen sicheren Ort, leider zu sich. | 98.04 |
| 1.7B-CustomVoice/german_custom_02_r4 | Ich legte die Schlüssel an einen sicheren Ort, leider zu sicher. | Ich legte die Schlüssel in einen sicheren Ort. Leider zu sicher. | 98.08 |
| 1.7B-CustomVoice/italian_custom_02_r2 | Ho messo le chiavi in un posto sicuro, forse troppo sicuro. | Ho messo le chiavi in un posto sicuro, forse è troppo sicuro. | 98.95 |
| 1.7B-CustomVoice/french_custom_01_r1 | Le café du matin a négocié ferme, puis il a accepté de m'aider. | Le café du matin a négocié fermes puis il a accepté de m'aider. | 98.97 |
| 1.7B-CustomVoice/russian_custom_02_r2 | Я положил ключи в надежное место, кажется, слишком надежное. | Я положил ключ в надежное место, кажется, слишком надежное. | 98.97 |
| 1.7B-CustomVoice/english_custom_01_r1 | The morning coffee negotiated hard, but eventually agreed to help. | The morning coffee negotiated hard, but eventually agreed to help. | 100.0 |

## faster / 1.7B-Base / complete

Image `sha256:908f3bcb2be48436d1bdaf273085f759d170b62f98102e44a8b7a8bc51b05631`; source `36fa150a0cff236e299313ba0bbb80eff74ba2c7af7dfd90b2a706901056c29b`.
API ready 2.047s; cold load 14.210s; discarded warmups 1. Incremental waveform support: True.

Resident cohort: `1.7B-Base`.
Cold load and memory cover the listed resident set. The full product run retains each checkpoint through its applicable suites, then unloads it before the next.

| Group | Judged | Exact % | Mean similarity % | Minimum % | Errors |
|---|---|---|---|---|---|
| Mode: clone | 30 | 6.67 | 96.75 | 83.92 | 0 |
| Language: Chinese | 3 | 0.0 | 97.31 | 96.77 | 0 |
| Language: English | 3 | 66.67 | 99.73 | 99.2 | 0 |
| Language: French | 3 | 0.0 | 94.19 | 83.92 | 0 |
| Language: German | 3 | 0.0 | 97.34 | 95.68 | 0 |
| Language: Italian | 3 | 0.0 | 97.84 | 95.92 | 0 |
| Language: Japanese | 3 | 0.0 | 99.42 | 99.42 | 0 |
| Language: Korean | 3 | 0.0 | 89.87 | 85.16 | 0 |
| Language: Portuguese | 3 | 0.0 | 99.07 | 98.25 | 0 |
| Language: Russian | 3 | 0.0 | 94.12 | 93.06 | 0 |
| Language: Spanish | 3 | 0.0 | 98.59 | 97.72 | 0 |

### Hardest calls

| Call | Expected | Transcript | Similarity % |
|---|---|---|---|
| 1.7B-Base/french_clone_01_r1 | Bonjour, voici VoxCPMTTS de Hangry Labs. Nous créons des outils vocaux locaux et faciles à lancer pour permettre de produire de la parole en privé, hors ligne et dans sa propre langue. | Bonjour, voici Vox EPMTTS de Hungry Labs. Nou crayon de zutit vocal loco est facile à lancer pour paramètre de traduire de la parole en privé, r ling et dans un propre lang. | 83.92 |
| 1.7B-Base/korean_clone_01_r3 | 안녕하세요, Hangry Labs의 VoxCPMTTS입니다. 우리는 사람들이 자신의 언어로, 개인적으로, 오프라인에서 음성을 만들 수 있도록 로컬에서 쉽게 실행되는 음성 도구를 만듭니다. | 안녕하세요, 핸그리 라이브의 복스시 PMTTS입니다. 우리는 사람들이 자신의 언어로 개인적으로 오프라인에서 음성을 만들 수 있도록 로컬에서 쉽게 실행되는 음성 도구를 만듭니다. | 85.16 |
| 1.7B-Base/korean_clone_01_r2 | 안녕하세요, Hangry Labs의 VoxCPMTTS입니다. 우리는 사람들이 자신의 언어로, 개인적으로, 오프라인에서 음성을 만들 수 있도록 로컬에서 쉽게 실행되는 음성 도구를 만듭니다. | 안녕하세요. 핸그리랩즈의 박 CPMTTS입니다. 우리는 사람들이 자신의 언어로 개인적으로 오프라인에서 음성을 만들 수 있도록 로컬에서 쉽게 실행되는 음성 도구를 만듭니다. | 87.58 |
| 1.7B-Base/russian_clone_01_r3 | Здравствуйте, это VoxCPMTTS от Hangry Labs. Мы создаем локальные и простые в запуске голосовые инструменты, чтобы люди могли создавать речь приватно, офлайн и на своем языке. | Здравствуйте, это Вок СПМ ТТС от Hungry Labs. Мы создаем локальные и простые в запуске голосовые инструменты, чтобы люди могли создавать речь приватно, офлайн и на своем языке. | 93.06 |
| 1.7B-Base/russian_clone_01_r2 | Здравствуйте, это VoxCPMTTS от Hangry Labs. Мы создаем локальные и простые в запуске голосовые инструменты, чтобы люди могли создавать речь приватно, офлайн и на своем языке. | Здравствуйте, это Vox с PMTTS от Hungary Labs. Мы создаем локальные и простые в запуске голосовые инструменты, чтобы люди могли создавать речь приватно, offline и на своем языке. | 93.79 |
| 1.7B-Base/russian_clone_01_r1 | Здравствуйте, это VoxCPMTTS от Hangry Labs. Мы создаем локальные и простые в запуске голосовые инструменты, чтобы люди могли создавать речь приватно, офлайн и на своем языке. | Здравствуйте, это Vox CPMTTS от Hangry Labs. Мы создаем локальные и простые в запуске голосовые инструменты, чтобы люди могли создавать речь приватно, offline и на своем языке. | 95.5 |
| 1.7B-Base/german_clone_01_r1 | Hallo, hier ist VoxCPMTTS von Hangry Labs. Wir bauen lokale, einfach startbare Sprachwerkzeuge, damit Menschen privat, offline und in ihrer eigenen Sprache Sprache erzeugen können. | Hallo, hier ist Vox PMTTS von Hengry Labs. Wir bauen lokale, einfach startbare Sprachverzögerer, damit Menschen privat, offline und in ihrer eigenen Sprachersprache erzeugen können. | 95.68 |
| 1.7B-Base/italian_clone_01_r3 | Ciao, questo è VoxCPMTTS di Hangry Labs. Costruiamo strumenti vocali locali e facili da avviare, così le persone possono creare parlato in privato, offline e nella propria lingua. | Ciao, questo è Vox CPMTTS di Hangry Labs. Costriamo strumenti vocali locali e facili da variare. Così le persone possono creare parlando in privato, offline, in alla propria lingua. | 95.92 |
| 1.7B-Base/chinese_clone_01_r2 | 你好，这里是 Hangry Labs 的 VoxCPMTTS。我们打造本地运行、容易使用的语音工具，让人们可以私密、离线地用自己的语言生成语音。 | 您好，这里是Hungry Labs的 Vox CPM TTS。我们打造本地运行、容易使用的语音工具，让人们可以私密、离线地用自己的语言生成语音。 | 96.77 |
| 1.7B-Base/chinese_clone_01_r3 | 你好，这里是 Hangry Labs 的 VoxCPMTTS。我们打造本地运行、容易使用的语音工具，让人们可以私密、离线地用自己的语言生成语音。 | 你好，这里是Hungry Labs的VoC CPM TTS。我们打造本地运行、容易使用的语音工具，让人们可以私密、离线地用自己的语言生成语音。 | 96.77 |
| 1.7B-Base/korean_clone_01_r1 | 안녕하세요, Hangry Labs의 VoxCPMTTS입니다. 우리는 사람들이 자신의 언어로, 개인적으로, 오프라인에서 음성을 만들 수 있도록 로컬에서 쉽게 실행되는 음성 도구를 만듭니다. | 안녕하세요, Henry Labs의 BoxC PMTTS입니다. 우리는 사람들이 자신의 언어로 개인적으로 오프라인에서 음성을 만들 수 있도록 로컬에서 쉽게 실행되는 음성 도구를 만듭니다. | 96.86 |
| 1.7B-Base/german_clone_01_r3 | Hallo, hier ist VoxCPMTTS von Hangry Labs. Wir bauen lokale, einfach startbare Sprachwerkzeuge, damit Menschen privat, offline und in ihrer eigenen Sprache Sprache erzeugen können. | Hallo, hier ist Vox CPM TTS von Hangry Labs, wir bauen lokale, einfach startbarisch Sprachverkzeuge, damit Menschen privat, offline und in ihrer eigenen Sprache Sprache erzeugen können. | 97.69 |
| 1.7B-Base/spanish_clone_01_r3 | Hola, esto es VoxCPMTTS de Hangry Labs. Creamos herramientas de voz locales y fáciles de ejecutar para que las personas puedan generar habla en privado, sin conexión y en su propio idioma. | Hola, esto es Vox CPM TTS The Hangry Labs. Creemos herramientas de voz locales y faciles de ejecutar para que las personas puedan generar habla en privado sin conexión y en su propio idioma. | 97.72 |
| 1.7B-Base/portuguese_clone_01_r1 | Olá, este é o VoxCPMTTS da Hangry Labs. Criamos ferramentas de voz locais e fáceis de executar para que as pessoas possam gerar fala com privacidade, offline e no próprio idioma. | Olá, este é o Vox PMTTS da Angry Labs. Criamos ferramentas de voz locais e fáceis de escutar para que as pessoas possam gerar fala com privacidade, offline e no próprio idioma. | 98.25 |
| 1.7B-Base/italian_clone_01_r1 | Ciao, questo è VoxCPMTTS di Hangry Labs. Costruiamo strumenti vocali locali e facili da avviare, così le persone possono creare parlato in privato, offline e nella propria lingua. | Ciao, Questo è Vox, SPM TTS di Hangry Labs. Costriamo strumenti vocali locali e facili da avviare. Così le persone possono creare parlato in privato, offline, inella propria lingua. | 98.29 |
| 1.7B-Base/chinese_clone_01_r1 | 你好，这里是 Hangry Labs 的 VoxCPMTTS。我们打造本地运行、容易使用的语音工具，让人们可以私密、离线地用自己的语言生成语音。 | 你好，这里是Hungry Labs的Vox CPM TTS。我们打造本地运行、容易使用的语音工具，让人们可以私密、离线地用自己的语言生成语音。 | 98.39 |
| 1.7B-Base/german_clone_01_r2 | Hallo, hier ist VoxCPMTTS von Hangry Labs. Wir bauen lokale, einfach startbare Sprachwerkzeuge, damit Menschen privat, offline und in ihrer eigenen Sprache Sprache erzeugen können. | Hallo, hier ist Vox CPM TTS von Angry Labs. Wir bauen lokale, einfach startbare Spracherzeuger, damit Menschen privat, offline und in ihrer eigenen Sprache Sprache erzeugen können. | 98.66 |
| 1.7B-Base/spanish_clone_01_r1 | Hola, esto es VoxCPMTTS de Hangry Labs. Creamos herramientas de voz locales y fáciles de ejecutar para que las personas puedan generar habla en privado, sin conexión y en su propio idioma. | Hola, esto es Vox SMTPTS de Hangry Labs. Creamos herramientas de voz locales y fáciles de ejecutar para que las personas puedan generar habla en privado, sin conexión y en su propio idioma. | 98.69 |
| 1.7B-Base/french_clone_01_r2 | Bonjour, voici VoxCPMTTS de Hangry Labs. Nous créons des outils vocaux locaux et faciles à lancer pour permettre de produire de la parole en privé, hors ligne et dans sa propre langue. | Bonjour, voici Vox CMPMTTS de Hungry Labs. Nous créons des outils vocaux locaux et faciles à lancer pour permettre de produire de la parole en privé, hors ligne et dans sa propre langue. | 99.0 |
| 1.7B-Base/english_clone_01_r3 | Hello, this is VoxCPMTTS from Hangry Labs. We build local, easy-to-run voice tools so people can create speech privately, offline, and in their own language. | Hello, this is Voxe PMTTS from Hangry Labs. We build local, easy to run voice tools so people can create speech privately, offline, and in their own language. | 99.2 |

## faster / 1.7B-VoiceDesign / complete

Image `sha256:908f3bcb2be48436d1bdaf273085f759d170b62f98102e44a8b7a8bc51b05631`; source `36fa150a0cff236e299313ba0bbb80eff74ba2c7af7dfd90b2a706901056c29b`.
API ready 2.068s; cold load 5.943s; discarded warmups 1. Incremental waveform support: True.

Resident cohort: `1.7B-VoiceDesign`.
Cold load and memory cover the listed resident set. The full product run retains each checkpoint through its applicable suites, then unloads it before the next.

| Group | Judged | Exact % | Mean similarity % | Minimum % | Errors |
|---|---|---|---|---|---|
| Mode: design | 100 | 90.0 | 99.58 | 90.91 | 0 |
| Language: Chinese | 10 | 80.0 | 98.18 | 90.91 | 0 |
| Language: English | 10 | 100.0 | 100.0 | 100.0 | 0 |
| Language: French | 10 | 80.0 | 99.79 | 98.95 | 0 |
| Language: German | 10 | 100.0 | 100.0 | 100.0 | 0 |
| Language: Italian | 10 | 100.0 | 100.0 | 100.0 | 0 |
| Language: Japanese | 10 | 90.0 | 99.47 | 94.74 | 0 |
| Language: Korean | 10 | 80.0 | 99.13 | 95.45 | 0 |
| Language: Portuguese | 10 | 90.0 | 99.64 | 96.39 | 0 |
| Language: Russian | 10 | 100.0 | 100.0 | 100.0 | 0 |
| Language: Spanish | 10 | 80.0 | 99.57 | 97.67 | 0 |

### Hardest calls

| Call | Expected | Transcript | Similarity % |
|---|---|---|---|
| 1.7B-VoiceDesign/chinese_design_02_r1 | 钥匙被我放在安全的地方，安全到连我自己都找不到。 | 要是被我放在安全的地方，安全到连我自己都找不到。 | 90.91 |
| 1.7B-VoiceDesign/chinese_design_02_r2 | 钥匙被我放在安全的地方，安全到连我自己都找不到。 | 要是被我放在安全的地方，安全到连我自己都找不到。 | 90.91 |
| 1.7B-VoiceDesign/japanese_design_02_r1 | 鍵を安全な場所に置いたら、安全すぎて自分でも見つかりません。 | 地獄を安全な場所に置いたら安全すぎて自分でも見つかりません。 | 94.74 |
| 1.7B-VoiceDesign/korean_design_01_r1 | 아침 커피는 조금 버텼지만 결국 나를 도와주었습니다. | 아침 커피는 조금 버렸지만 결국 나를 도와주었습니다. | 95.45 |
| 1.7B-VoiceDesign/korean_design_02_r2 | 열쇠를 안전한 곳에 두었더니 너무 안전해서 못 찾겠습니다. | 열쇠를 안전한 곳에 두웠더니 너무 안전해서 못 찾겠습니다. | 95.83 |
| 1.7B-VoiceDesign/portuguese_design_02_r2 | Guardei as chaves em um lugar seguro, seguro demais. | Guarda as chaves em um lugar seguro, seguro demais. | 96.39 |
| 1.7B-VoiceDesign/spanish_design_01_r1 | El café de la mañana negoció duro, pero al final ayudó. | El café de la mañana negocio duro, pero al final ayudó. | 97.67 |
| 1.7B-VoiceDesign/spanish_design_02_r3 | Guardé las llaves en un lugar seguro, quizá demasiado seguro. | Guardé las llaves en un lugar seguro. Ah, quizá demasiado seguro. | 98.04 |
| 1.7B-VoiceDesign/french_design_01_r4 | Le café du matin a négocié ferme, puis il a accepté de m'aider. | Le café du matin a négocié ferm, puis il a accepté de m'aider. | 98.95 |
| 1.7B-VoiceDesign/french_design_01_r3 | Le café du matin a négocié ferme, puis il a accepté de m'aider. | Le café du matin a négocié fermes puis il a accepté de m'aider. | 98.97 |
| 1.7B-VoiceDesign/english_design_01_r1 | The morning coffee negotiated hard, but eventually agreed to help. | The morning coffee negotiated hard, but eventually agreed to help. | 100.0 |
| 1.7B-VoiceDesign/english_design_01_r2 | The morning coffee negotiated hard, but eventually agreed to help. | The morning coffee negotiated hard, but eventually agreed to help. | 100.0 |
| 1.7B-VoiceDesign/english_design_01_r3 | The morning coffee negotiated hard, but eventually agreed to help. | The morning coffee negotiated hard, but eventually agreed to help. | 100.0 |
| 1.7B-VoiceDesign/english_design_01_r4 | The morning coffee negotiated hard, but eventually agreed to help. | The morning coffee negotiated hard, but eventually agreed to help. | 100.0 |
| 1.7B-VoiceDesign/english_design_01_r5 | The morning coffee negotiated hard, but eventually agreed to help. | The morning coffee negotiated hard, but eventually agreed to help. | 100.0 |
| 1.7B-VoiceDesign/english_design_02_r1 | I put my keys somewhere safe, which was a bold move against myself. | I put my keys somewhere safe, which was a bold move against myself. | 100.0 |
| 1.7B-VoiceDesign/english_design_02_r2 | I put my keys somewhere safe, which was a bold move against myself. | I put my keys somewhere safe, which was a bold move against myself. | 100.0 |
| 1.7B-VoiceDesign/english_design_02_r3 | I put my keys somewhere safe, which was a bold move against myself. | I put my keys somewhere safe, which was a bold move against myself. | 100.0 |
| 1.7B-VoiceDesign/english_design_02_r4 | I put my keys somewhere safe, which was a bold move against myself. | I put my keys somewhere safe, which was a bold move against myself. | 100.0 |
| 1.7B-VoiceDesign/english_design_02_r5 | I put my keys somewhere safe, which was a bold move against myself. | I put my keys somewhere safe, which was a bold move against myself. | 100.0 |

