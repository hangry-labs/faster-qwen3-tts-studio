<p align="center">
  <img src="src/faster_qwen3_tts/standalone_ui/assets/qwen3_tts_logo_horizontal.webp" alt="Hangry Labs Faster Qwen3-TTS Studio" width="900">
</p>

<p align="center"><a href="README.md">English</a> · <strong>Norsk bokmål</strong> · <a href="README.pl.md">Polski</a> · <a href="README.ja.md">日本語</a> · <a href="README.zh.md">简体中文</a> · <a href="README.es.md">Español</a></p>

<p align="center"><a href="https://hangry-labs.github.io/faster-qwen3-tts-studio/examples/?lang=nb"><strong>🎧 Lytt til stemmeeksempler</strong></a></p>

# Hangry Labs Faster Qwen3-TTS Studio

Lokal stemmedesign, stemmekloning og talegenerering med Qwen3-TTS i en Docker-pakket Studio med nettlesergrensesnitt, strømmet avspilling og HTTP-API.

Gjeldende versjon, endringshistorikk og publiseringsstatus finnes i [den engelske hoveddokumentasjonen](README.md).

## Hurtigstart

Har du Docker, NVIDIA GPU-støtte og en driver som støtter CUDA 12.8, trenger du bare én kommando:

```bash
docker run -d --name faster-qwen3-tts-studio --restart unless-stopped -p 127.0.0.1:7860:7860 --gpus all -e CUDA_VISIBLE_DEVICES=0 -v faster_qwen3_tts_studio_data:/app/persistent hangrylabs/faster-qwen3-tts-studio:v1.0@sha256:a8a3643b077e05c2ccf33e9b97978f082d2e89ac33b3d1368ab0e25df628899d
```

Åpne **[http://localhost:7860](http://localhost:7860)** og begynn å generere tale. Det komplette bildet inneholder alle fem fastlåste modeller og kan kjøre uten nett etter nedlastingen. Volumet beholder modeller, lagrede stemmer og manus.

<details markdown="1">
<summary><strong>Mindre nedlasting: tiny-bildet</strong></summary>

```bash
docker run -d --name faster-qwen3-tts-studio --restart unless-stopped -p 127.0.0.1:7860:7860 --gpus all -e CUDA_VISIBLE_DEVICES=0 -v faster_qwen3_tts_studio_data:/app/persistent hangrylabs/faster-qwen3-tts-studio:v1.0_tiny@sha256:29f06b3226da4a55244727e111e7700786e53049a54560efeef4bb12a62bd0bd
```

Tiny laster ned modeller til samme volum ved første bruk. Behold nettilgang til de valgte modellene er lagret. Velg enten full eller tiny.

</details>

Du trenger ikke Git, Python på vertsmaskinen eller manuell modellinstallasjon. Se [bygging fra kildekode](docs/DEVELOPMENT.md#build-from-source) for utvikling, [API-visningen](http://localhost:7860/docs) og [Docker Hub-veiledningen](docs/dockerhub.md) for flere detaljer.

<p align="center">
  <a href="assets/screenshots/generate-ui.webp">
    <img src="assets/screenshots/generate-ui.webp" alt="Qwen3-TTS Studio med Magic-dialog, stemmeinnstillinger og lagrede manus" width="1200">
  </a>
</p>

## Dette får du

- Design stemmer fra beskrivelser med 1.7B VoiceDesign.
- Klon tillatte referanseopptak med 0.6B eller 1.7B Base, med valgfri eksperimentell regi.
- Generer tale med ni innebygde CustomVoice-stemmer; regiinstruksjoner krever 1.7B.
- Rediger tekst, SSML, SSML-H og Magic-dialoger med replikker, karakterer og gjenbrukbare opptak.
- Lagre stemmer med portrett, etiketter, original og behandlet referanse samt opprettingsinnstillinger for senere finjustering.
- Last opp eller ta opp lyd, trim bølgeformer, bruk FFmpeg-effekter og lagre ferdig lyd.
- Bruk OpenAI-kompatibel tale, native API-er og valgfritt kompakt eller avansert MCP.
- Inspiser kø, avbryt generering og styr modeller og GPU-minne fra System.

Grensesnittet finnes på engelsk, norsk bokmål, polsk, japansk, forenklet kinesisk og spansk. Du kan bytte språk uten å miste tekst, referanseopptak eller generert lyd. Valget lagres lokalt i nettleseren. Direkte språklenke: [/nb](http://localhost:7860/nb).

**Grensesnittspråk og talespråk er ulike valg.** Qwen støtter kinesisk, engelsk, japansk, koreansk, tysk, fransk, russisk, portugisisk, spansk og italiensk, samt automatisk språkvalg. Norsk og polsk er grensesnittspråk, ikke støttede talespråk. Eksempler følger valgt talespråk; Auto bruker engelsk eksempeltekst.

## Modeller og minne

| Familie | Størrelser | Bruk |
| --- | --- | --- |
| Base | 0.6B, 1.7B | Kloning fra referanselyd |
| CustomVoice | 0.6B, 1.7B | Ni innebygde stemmer |
| VoiceDesign | 1.7B | Ny stemme fra beskrivelse |

Standardinnstillingene beholder 0.6B Base, 0.6B CustomVoice og 1.7B VoiceDesign i GPU-minnet. Velg standardmodell og alltid lastet per arbeidsflyt i System, eller slå av minnebevaring. Modellene deler én seriell inferenskø. Maskinvaremålet er NVIDIA med Torch, Python 3.13 og CUDA 12.8.

Bruk nøyaktig referansetranskripsjon for best mulig kloning. Base-regi er eksperimentell og kan ignoreres når bare stemmeidentitet brukes. Ekstern ASR er valgfri og må konfigureres; ingen lokal ASR-modell startes.

## API

```bash
curl http://localhost:7860/v1/audio/speech -H "Content-Type: application/json" -d '{"model":"qwen3-tts","input":"Hello from Qwen Studio.","voice":"Ryan","response_format":"mp3"}' --output speech.mp3
```

Tale-API-et støtter MP3, WAV, FLAC, Opus, AAC, Ogg og PCM. Nettleserstrømming bruker MP3. Se [API-veiledningen](docs/API.md), [SSML-H](docs/SSML-H.md), [MCP-verktøyene](docs/MCP.md) og [Studio-veiledningen](docs/STUDIO.md). Disse tekniske veiledningene vedlikeholdes på engelsk.

## Personvern og ansvarlig bruk

Klon bare stemmer med samtykke, og ikke bruk syntetisk tale til villedende etterligning. Referanser og manus lagres bare når du velger å lagre dem. MCP-lydlenker er midlertidige. Ekstern ASR mottar opptakene du uttrykkelig sender til transkripsjon; velg en tjeneste du stoler på. Behold lokal portbinding, eller beskytt en nettverkseksponert tjeneste med autentisering og en egnet proxy.

## Målinger, oppstrøm og lisenser

Målte hastigheter, VRAM og strømmelatens finnes i [benchmark-oversikten](benchmarks/README.md). Historikk er ikke en garanti for alle GPU-er eller stemmer.

Vi vedlikeholder lokal inferenskode, akselerasjon, Studio og integrasjoner på grunnlag av [Qwen3-TTS](https://github.com/QwenLM/Qwen3-TTS), [kompatibilitetsgrenen qwen-tts-hf](https://github.com/andimarafioti/Qwen3-TTS/tree/distribution/qwen-tts-hf) og [faster-qwen3-tts](https://github.com/andimarafioti/faster-qwen3-tts). Se [opprinnelse og synkronisering](docs/UPSTREAMS.md).

Prosjektkoden bruker Apache-2.0. Modeller og hele Docker-distribusjonen har flere komponentvilkår; [LICENSE](LICENSE), [NOTICE](NOTICE), [tredjepartsmerknader](THIRD_PARTY_NOTICES.md) og [lisensveiledningen](docs/LICENSING.md) beskriver dem. Prosjektlisensen erstatter ikke disse pliktene.

<details markdown="1">
<summary>Versjonshistorikk</summary>

Den oppdaterte, samlede [versjonshistorikken](README.md#version-history) vedlikeholdes i hoveddokumentasjonen.

</details>
