window.LANGUAGE_META = {
  "english": {
    "nativeName": "English",
    "icon": "EN"
  },
  "chinese": {
    "nativeName": "中文",
    "icon": "中"
  },
  "japanese": {
    "nativeName": "日本語",
    "icon": "日"
  },
  "korean": {
    "nativeName": "한국어",
    "icon": "한"
  },
  "german": {
    "nativeName": "Deutsch",
    "icon": "DE"
  },
  "french": {
    "nativeName": "Français",
    "icon": "FR"
  },
  "russian": {
    "nativeName": "Русский",
    "icon": "RU"
  },
  "portuguese": {
    "nativeName": "Português",
    "icon": "PT"
  },
  "spanish": {
    "nativeName": "Español",
    "icon": "ES"
  },
  "italian": {
    "nativeName": "Italiano",
    "icon": "IT"
  }
};
window.EXAMPLE_MANIFEST = {
  "schema_version": 1,
  "project_name": "Faster Qwen3-TTS Studio",
  "generated_at": "2026-10-27T07:22:18.911427+00:00",
  "definitions_sha256": "c2a712a6bc7a9ae703aed3a4dbebca9dd23312d8265dac13ebcc9a013faefc8e",
  "models": {
    "design": {
      "id": "Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign",
      "revision": "5ecdb67327fd37bb2e042aab12ff7391903235d3"
    },
    "clone": {
      "id": "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
      "revision": "fd4b254389122332181a7c3db7f27e918eec64e3"
    }
  },
  "voices": [
    {
      "id": "warm_female_narrator",
      "label": "Warm female narrator",
      "design": {
        "language": "English",
        "text": "The little bookshop was quiet when I arrived. Outside, the rain had stopped, and warm sunlight was finding its way through the windows.",
        "instruct": "A warm adult woman with a rich middle register, gentle breath, clear diction and an inviting storytelling rhythm.",
        "seed": 7300
      },
      "references": {
        "english": {
          "file": "references/warm_female_narrator.flac",
          "text": "The little bookshop was quiet when I arrived. Outside, the rain had stopped, and warm sunlight was finding its way through the windows.",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "language": "English",
              "text": "The little bookshop was quiet when I arrived. Outside, the rain had stopped, and warm sunlight was finding its way through the windows.",
              "instruct": "A warm adult woman with a rich middle register, gentle breath, clear diction and an inviting storytelling rhythm.",
              "seed": 7300,
              "mode": "design",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign",
              "non_streaming_mode": true
            },
            "model_revision": "5ecdb67327fd37bb2e042aab12ff7391903235d3",
            "reference_sha256": null
          },
          "fingerprint": "2578d48944e98823a7e2ab263ed44bcc2fbd7f4e9820dc08de79bd6ddb2422d7",
          "sha256": "591dc509d7be0360448d36b7a16f4e5bc8587d6096af849ffb37a69a298d7075",
          "bytes": 215828,
          "duration_seconds": 7.92
        },
        "chinese": {
          "file": "references/chinese/warm_female_narrator.flac",
          "text": "雨刚停，街道像重新打开的一页纸。 夜里的茶壶很安静，但好像什么都明白。",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "language": "Chinese",
              "text": "雨刚停，街道像重新打开的一页纸。 夜里的茶壶很安静，但好像什么都明白。",
              "instruct": "A warm adult woman with a rich middle register, gentle breath, clear diction and an inviting storytelling rhythm.",
              "seed": 7400,
              "mode": "design",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign",
              "non_streaming_mode": true
            },
            "model_revision": "5ecdb67327fd37bb2e042aab12ff7391903235d3",
            "reference_sha256": null
          },
          "fingerprint": "6de64b47230a2f927d1afdbe34c3d03451e2109e03cc4ca9e653184f8f442351",
          "sha256": "fca1966c27de4771410321fdc9ee9171f314d901d1606de4c64dd430b090cb75",
          "bytes": 202042,
          "duration_seconds": 7.76
        },
        "japanese": {
          "file": "references/japanese/warm_female_narrator.flac",
          "text": "雨上がりの道は、新しい一日のページみたいでした。 夕方の風で、街の音が少しやわらぎました。",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "language": "Japanese",
              "text": "雨上がりの道は、新しい一日のページみたいでした。 夕方の風で、街の音が少しやわらぎました。",
              "instruct": "A warm adult woman with a rich middle register, gentle breath, clear diction and an inviting storytelling rhythm.",
              "seed": 7500,
              "mode": "design",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign",
              "non_streaming_mode": true
            },
            "model_revision": "5ecdb67327fd37bb2e042aab12ff7391903235d3",
            "reference_sha256": null
          },
          "fingerprint": "7c01b326a3fc80690012d1f615bbafc7fcd27927ae5187846dd4744ff20d3c2d",
          "sha256": "858254f8ecd8a0e123fc9b224aaac7510c305126439d1229dfd10f86fd60e79c",
          "bytes": 242068,
          "duration_seconds": 8.72
        },
        "korean": {
          "file": "references/korean/warm_female_narrator.flac",
          "text": "비가 그친 뒤 거리는 새로 시작하는 하루처럼 보였습니다. 저녁 바람이 도시의 소리를 조금 부드럽게 만들었습니다.",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "language": "Korean",
              "text": "비가 그친 뒤 거리는 새로 시작하는 하루처럼 보였습니다. 저녁 바람이 도시의 소리를 조금 부드럽게 만들었습니다.",
              "instruct": "A warm adult woman with a rich middle register, gentle breath, clear diction and an inviting storytelling rhythm.",
              "seed": 7600,
              "mode": "design",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign",
              "non_streaming_mode": true
            },
            "model_revision": "5ecdb67327fd37bb2e042aab12ff7391903235d3",
            "reference_sha256": null
          },
          "fingerprint": "100810452c46256454b87f5f913d5d0bdb2280ba13249f233ba8bb3eb856d797",
          "sha256": "2aad3deb93752c5ea50d789dc56844e13bd6ac76cca9484057f47f3b54f41d74",
          "bytes": 258359,
          "duration_seconds": 9.44
        },
        "german": {
          "file": "references/german/warm_female_narrator.flac",
          "text": "Nach dem Regen sah die Straße aus wie ein neuer Anfang. Der Abendwind machte die Stadt ein wenig freundlicher.",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "language": "German",
              "text": "Nach dem Regen sah die Straße aus wie ein neuer Anfang. Der Abendwind machte die Stadt ein wenig freundlicher.",
              "instruct": "A warm adult woman with a rich middle register, gentle breath, clear diction and an inviting storytelling rhythm.",
              "seed": 7700,
              "mode": "design",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign",
              "non_streaming_mode": true
            },
            "model_revision": "5ecdb67327fd37bb2e042aab12ff7391903235d3",
            "reference_sha256": null
          },
          "fingerprint": "4537741cab9d9ac9957055c9ee58f9e136c500a4a4e9dec9a36ede48c3b110c0",
          "sha256": "62f2514f9aaa43b9695c8dc9190d3fbd431ca13ddcb4573e4f7065cb37b3224d",
          "bytes": 189193,
          "duration_seconds": 6.64
        },
        "french": {
          "file": "references/french/warm_female_narrator.flac",
          "text": "Après la pluie, la rue semblait recommencer la journée. Le vent du soir a rendu la ville un peu plus douce.",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "language": "French",
              "text": "Après la pluie, la rue semblait recommencer la journée. Le vent du soir a rendu la ville un peu plus douce.",
              "instruct": "A warm adult woman with a rich middle register, gentle breath, clear diction and an inviting storytelling rhythm.",
              "seed": 7800,
              "mode": "design",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign",
              "non_streaming_mode": true
            },
            "model_revision": "5ecdb67327fd37bb2e042aab12ff7391903235d3",
            "reference_sha256": null
          },
          "fingerprint": "e0950522cc1d35c73daed5537f989e1ff3c1a0a7e10cfaf0e735eaa9fa0e5b7a",
          "sha256": "5818fe66d8f782933a08fb088588638f1167024329f79017d85d87d9664d92d2",
          "bytes": 193684,
          "duration_seconds": 7.04
        },
        "russian": {
          "file": "references/russian/warm_female_narrator.flac",
          "text": "После дождя улица выглядела как новое начало. Вечерний ветер сделал город немного спокойнее.",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "language": "Russian",
              "text": "После дождя улица выглядела как новое начало. Вечерний ветер сделал город немного спокойнее.",
              "instruct": "A warm adult woman with a rich middle register, gentle breath, clear diction and an inviting storytelling rhythm.",
              "seed": 7900,
              "mode": "design",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign",
              "non_streaming_mode": true
            },
            "model_revision": "5ecdb67327fd37bb2e042aab12ff7391903235d3",
            "reference_sha256": null
          },
          "fingerprint": "f948681df766554c62584f1bbf1ba7eef0ad5ee2be105fb9c9da3b7329b870f8",
          "sha256": "441147203cee79ec1c438aedf32696f8de4c1e266e1c6ca3fefd9641d80d4cbf",
          "bytes": 194233,
          "duration_seconds": 6.48
        },
        "portuguese": {
          "file": "references/portuguese/warm_female_narrator.flac",
          "text": "Depois da chuva, a rua parecia um novo começo. O vento da tarde deixou a cidade um pouco mais calma.",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "language": "Portuguese",
              "text": "Depois da chuva, a rua parecia um novo começo. O vento da tarde deixou a cidade um pouco mais calma.",
              "instruct": "A warm adult woman with a rich middle register, gentle breath, clear diction and an inviting storytelling rhythm.",
              "seed": 8000,
              "mode": "design",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign",
              "non_streaming_mode": true
            },
            "model_revision": "5ecdb67327fd37bb2e042aab12ff7391903235d3",
            "reference_sha256": null
          },
          "fingerprint": "a0aef6d8bed1e48260bd9f2c9a96bc320c7290060c68d86d9601ad6bb782c082",
          "sha256": "76fa1c7387e61798edc751a02f74763dbd4498673e02458085a9c1f126d6c050",
          "bytes": 213186,
          "duration_seconds": 8.48
        },
        "spanish": {
          "file": "references/spanish/warm_female_narrator.flac",
          "text": "Después de la lluvia, la calle parecía un nuevo comienzo. El viento de la tarde hizo que la ciudad sonara más tranquila.",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "language": "Spanish",
              "text": "Después de la lluvia, la calle parecía un nuevo comienzo. El viento de la tarde hizo que la ciudad sonara más tranquila.",
              "instruct": "A warm adult woman with a rich middle register, gentle breath, clear diction and an inviting storytelling rhythm.",
              "seed": 8100,
              "mode": "design",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign",
              "non_streaming_mode": true
            },
            "model_revision": "5ecdb67327fd37bb2e042aab12ff7391903235d3",
            "reference_sha256": null
          },
          "fingerprint": "fb26187a7c3e3780a25ad249c3f23b19a46c2ec49b3cfcf0aa12d5eb8cd0f2e0",
          "sha256": "6bcaeb53a66afce2196e4d80d21cad60b774c0a02c2c16be73a9de4278b67e86",
          "bytes": 237591,
          "duration_seconds": 8.0
        },
        "italian": {
          "file": "references/italian/warm_female_narrator.flac",
          "text": "Dopo la pioggia, la strada sembrava un nuovo inizio. Il vento della sera ha reso la città più calma.",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "language": "Italian",
              "text": "Dopo la pioggia, la strada sembrava un nuovo inizio. Il vento della sera ha reso la città più calma.",
              "instruct": "A warm adult woman with a rich middle register, gentle breath, clear diction and an inviting storytelling rhythm.",
              "seed": 8200,
              "mode": "design",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign",
              "non_streaming_mode": true
            },
            "model_revision": "5ecdb67327fd37bb2e042aab12ff7391903235d3",
            "reference_sha256": null
          },
          "fingerprint": "f3b603709f6bb5735a4a3586d02463e49eb8bc3d0cdb426e1d64aa47b277946c",
          "sha256": "06d71f977084e685527eae941a29ac1416ecc553c7a9b8ce1168f1c46b2ba266",
          "bytes": 215118,
          "duration_seconds": 7.76
        }
      },
      "reference": {
        "file": "references/warm_female_narrator.flac",
        "text": "The little bookshop was quiet when I arrived. Outside, the rain had stopped, and warm sunlight was finding its way through the windows.",
        "recipe": {
          "request": {
            "temperature": 0.9,
            "top_k": 50,
            "repetition_penalty": 1.05,
            "max_new_tokens": 600,
            "chunk_size": 8,
            "decoder_context_frames": 25,
            "language": "English",
            "text": "The little bookshop was quiet when I arrived. Outside, the rain had stopped, and warm sunlight was finding its way through the windows.",
            "instruct": "A warm adult woman with a rich middle register, gentle breath, clear diction and an inviting storytelling rhythm.",
            "seed": 7300,
            "mode": "design",
            "model": "Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign",
            "non_streaming_mode": true
          },
          "model_revision": "5ecdb67327fd37bb2e042aab12ff7391903235d3",
          "reference_sha256": null
        },
        "fingerprint": "2578d48944e98823a7e2ab263ed44bcc2fbd7f4e9820dc08de79bd6ddb2422d7",
        "sha256": "591dc509d7be0360448d36b7a16f4e5bc8587d6096af849ffb37a69a298d7075",
        "bytes": 215828,
        "duration_seconds": 7.92
      }
    },
    {
      "id": "calm_male_narrator",
      "label": "Calm male narrator",
      "design": {
        "language": "English",
        "text": "The little bookshop was quiet when I arrived. Outside, the rain had stopped, and warm sunlight was finding its way through the windows.",
        "instruct": "A calm adult man with a resonant baritone, unhurried phrasing and a reassuring, softly textured voice.",
        "seed": 7301
      },
      "references": {
        "english": {
          "file": "references/calm_male_narrator.flac",
          "text": "The little bookshop was quiet when I arrived. Outside, the rain had stopped, and warm sunlight was finding its way through the windows.",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "language": "English",
              "text": "The little bookshop was quiet when I arrived. Outside, the rain had stopped, and warm sunlight was finding its way through the windows.",
              "instruct": "A calm adult man with a resonant baritone, unhurried phrasing and a reassuring, softly textured voice.",
              "seed": 7301,
              "mode": "design",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign",
              "non_streaming_mode": true
            },
            "model_revision": "5ecdb67327fd37bb2e042aab12ff7391903235d3",
            "reference_sha256": null
          },
          "fingerprint": "7f63b92bbf320eb440c159241f571e0fd691b2cbb2fd2388207be8657311dea7",
          "sha256": "dc0b1558e47ab5be575a9fa57cb85dc6612e437431d6d87d14ed05e4f15c21bb",
          "bytes": 265149,
          "duration_seconds": 10.56
        },
        "chinese": {
          "file": "references/chinese/calm_male_narrator.flac",
          "text": "雨刚停，街道像重新打开的一页纸。 夜里的茶壶很安静，但好像什么都明白。",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "language": "Chinese",
              "text": "雨刚停，街道像重新打开的一页纸。 夜里的茶壶很安静，但好像什么都明白。",
              "instruct": "A calm adult man with a resonant baritone, unhurried phrasing and a reassuring, softly textured voice.",
              "seed": 7401,
              "mode": "design",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign",
              "non_streaming_mode": true
            },
            "model_revision": "5ecdb67327fd37bb2e042aab12ff7391903235d3",
            "reference_sha256": null
          },
          "fingerprint": "1916918ba16333aa9bff2cc15ae30eb00c53f22beccdd7154d4d14596a4abc76",
          "sha256": "267600e7ddcafe29cb8cac88952cf32ef3ff8c621ab5e3fbff2ab7c0973c35e3",
          "bytes": 278455,
          "duration_seconds": 10.96
        },
        "japanese": {
          "file": "references/japanese/calm_male_narrator.flac",
          "text": "雨上がりの道は、新しい一日のページみたいでした。 夕方の風で、街の音が少しやわらぎました。",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "language": "Japanese",
              "text": "雨上がりの道は、新しい一日のページみたいでした。 夕方の風で、街の音が少しやわらぎました。",
              "instruct": "A calm adult man with a resonant baritone, unhurried phrasing and a reassuring, softly textured voice.",
              "seed": 7501,
              "mode": "design",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign",
              "non_streaming_mode": true
            },
            "model_revision": "5ecdb67327fd37bb2e042aab12ff7391903235d3",
            "reference_sha256": null
          },
          "fingerprint": "97236c0deb301591c03ea97cf89df43321f560f72b8117074b80abc4fc800bbe",
          "sha256": "6f72d2c0fc2df41ec20b501823fefd7a6880509662a0c2c2e22f5c55790ad193",
          "bytes": 225827,
          "duration_seconds": 8.88
        },
        "korean": {
          "file": "references/korean/calm_male_narrator.flac",
          "text": "비가 그친 뒤 거리는 새로 시작하는 하루처럼 보였습니다. 저녁 바람이 도시의 소리를 조금 부드럽게 만들었습니다.",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "language": "Korean",
              "text": "비가 그친 뒤 거리는 새로 시작하는 하루처럼 보였습니다. 저녁 바람이 도시의 소리를 조금 부드럽게 만들었습니다.",
              "instruct": "A calm adult man with a resonant baritone, unhurried phrasing and a reassuring, softly textured voice.",
              "seed": 7601,
              "mode": "design",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign",
              "non_streaming_mode": true
            },
            "model_revision": "5ecdb67327fd37bb2e042aab12ff7391903235d3",
            "reference_sha256": null
          },
          "fingerprint": "6ad2c18bc56f3acd2610095596732c838ad69d3a49d5364b9f926c4dcecf8029",
          "sha256": "cb1af396f7c17621f7c4290507f7292aa0f3fafe67728ad6340486d0dfaf535e",
          "bytes": 229396,
          "duration_seconds": 9.36
        },
        "german": {
          "file": "references/german/calm_male_narrator.flac",
          "text": "Nach dem Regen sah die Straße aus wie ein neuer Anfang. Der Abendwind machte die Stadt ein wenig freundlicher.",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "language": "German",
              "text": "Nach dem Regen sah die Straße aus wie ein neuer Anfang. Der Abendwind machte die Stadt ein wenig freundlicher.",
              "instruct": "A calm adult man with a resonant baritone, unhurried phrasing and a reassuring, softly textured voice.",
              "seed": 7701,
              "mode": "design",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign",
              "non_streaming_mode": true
            },
            "model_revision": "5ecdb67327fd37bb2e042aab12ff7391903235d3",
            "reference_sha256": null
          },
          "fingerprint": "3ce4c87bd6c499a83b7b3ebbbaea866290ca9f9befe6b6743700ad4827bb28ce",
          "sha256": "9e1b9440d2894db533c18fdf2e4200d4396aeb28f9a1dadf41e65a3bb12944c1",
          "bytes": 204988,
          "duration_seconds": 7.76
        },
        "french": {
          "file": "references/french/calm_male_narrator.flac",
          "text": "Après la pluie, la rue semblait recommencer la journée. Le vent du soir a rendu la ville un peu plus douce.",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "language": "French",
              "text": "Après la pluie, la rue semblait recommencer la journée. Le vent du soir a rendu la ville un peu plus douce.",
              "instruct": "A calm adult man with a resonant baritone, unhurried phrasing and a reassuring, softly textured voice.",
              "seed": 7801,
              "mode": "design",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign",
              "non_streaming_mode": true
            },
            "model_revision": "5ecdb67327fd37bb2e042aab12ff7391903235d3",
            "reference_sha256": null
          },
          "fingerprint": "fc648a7a0d04ff2ff410be764fddd886a925bb801eadec48adf34d7b07b8174a",
          "sha256": "bce239e649a97d17ee98b16cc8a8e1b78a10337266c8c5ffe72c9fde8a2b9d60",
          "bytes": 160348,
          "duration_seconds": 6.88
        },
        "russian": {
          "file": "references/russian/calm_male_narrator.flac",
          "text": "После дождя улица выглядела как новое начало. Вечерний ветер сделал город немного спокойнее.",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "language": "Russian",
              "text": "После дождя улица выглядела как новое начало. Вечерний ветер сделал город немного спокойнее.",
              "instruct": "A calm adult man with a resonant baritone, unhurried phrasing and a reassuring, softly textured voice.",
              "seed": 7901,
              "mode": "design",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign",
              "non_streaming_mode": true
            },
            "model_revision": "5ecdb67327fd37bb2e042aab12ff7391903235d3",
            "reference_sha256": null
          },
          "fingerprint": "e782d7a72881fdb2d1af5331243a3080fdf72b70ee14d060516da58cf5f3698c",
          "sha256": "4233ff17ed54096b005774825ffefcfe79670d679e97fda7ae54ec73bc5ec5ef",
          "bytes": 225265,
          "duration_seconds": 7.28
        },
        "portuguese": {
          "file": "references/portuguese/calm_male_narrator.flac",
          "text": "Depois da chuva, a rua parecia um novo começo. O vento da tarde deixou a cidade um pouco mais calma.",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "language": "Portuguese",
              "text": "Depois da chuva, a rua parecia um novo começo. O vento da tarde deixou a cidade um pouco mais calma.",
              "instruct": "A calm adult man with a resonant baritone, unhurried phrasing and a reassuring, softly textured voice.",
              "seed": 8001,
              "mode": "design",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign",
              "non_streaming_mode": true
            },
            "model_revision": "5ecdb67327fd37bb2e042aab12ff7391903235d3",
            "reference_sha256": null
          },
          "fingerprint": "70cb380da0122fac6a88c3b0af22cf872366eed9e9dc174210fb694d22a921da",
          "sha256": "59fc5b42df9f5e4d4ac9597ca066d058be67152950e942ad3b895e2c804236bb",
          "bytes": 171506,
          "duration_seconds": 6.72
        },
        "spanish": {
          "file": "references/spanish/calm_male_narrator.flac",
          "text": "Después de la lluvia, la calle parecía un nuevo comienzo. El viento de la tarde hizo que la ciudad sonara más tranquila.",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "language": "Spanish",
              "text": "Después de la lluvia, la calle parecía un nuevo comienzo. El viento de la tarde hizo que la ciudad sonara más tranquila.",
              "instruct": "A calm adult man with a resonant baritone, unhurried phrasing and a reassuring, softly textured voice.",
              "seed": 8101,
              "mode": "design",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign",
              "non_streaming_mode": true
            },
            "model_revision": "5ecdb67327fd37bb2e042aab12ff7391903235d3",
            "reference_sha256": null
          },
          "fingerprint": "62c59295b43bb0e79fa425c5952c8bb7aa5bb030d69da5614152d538a1aed07d",
          "sha256": "974855305359426667a36aaa0ebeb9cfcc812ebe0ac4bc164eafa30baaf57253",
          "bytes": 181795,
          "duration_seconds": 7.2
        },
        "italian": {
          "file": "references/italian/calm_male_narrator.flac",
          "text": "Dopo la pioggia, la strada sembrava un nuovo inizio. Il vento della sera ha reso la città più calma.",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "language": "Italian",
              "text": "Dopo la pioggia, la strada sembrava un nuovo inizio. Il vento della sera ha reso la città più calma.",
              "instruct": "A calm adult man with a resonant baritone, unhurried phrasing and a reassuring, softly textured voice.",
              "seed": 8201,
              "mode": "design",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign",
              "non_streaming_mode": true
            },
            "model_revision": "5ecdb67327fd37bb2e042aab12ff7391903235d3",
            "reference_sha256": null
          },
          "fingerprint": "7c712efb1f38ad77516e112fb55b927a0318b0a91963814740b7321c23f2ba6e",
          "sha256": "697133a044e702be36589cd32f0339207cff4f4a27d1ebfe78fbd7306588230c",
          "bytes": 196728,
          "duration_seconds": 6.96
        }
      },
      "reference": {
        "file": "references/calm_male_narrator.flac",
        "text": "The little bookshop was quiet when I arrived. Outside, the rain had stopped, and warm sunlight was finding its way through the windows.",
        "recipe": {
          "request": {
            "temperature": 0.9,
            "top_k": 50,
            "repetition_penalty": 1.05,
            "max_new_tokens": 600,
            "chunk_size": 8,
            "decoder_context_frames": 25,
            "language": "English",
            "text": "The little bookshop was quiet when I arrived. Outside, the rain had stopped, and warm sunlight was finding its way through the windows.",
            "instruct": "A calm adult man with a resonant baritone, unhurried phrasing and a reassuring, softly textured voice.",
            "seed": 7301,
            "mode": "design",
            "model": "Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign",
            "non_streaming_mode": true
          },
          "model_revision": "5ecdb67327fd37bb2e042aab12ff7391903235d3",
          "reference_sha256": null
        },
        "fingerprint": "7f63b92bbf320eb440c159241f571e0fd691b2cbb2fd2388207be8657311dea7",
        "sha256": "dc0b1558e47ab5be575a9fa57cb85dc6612e437431d6d87d14ed05e4f15c21bb",
        "bytes": 265149,
        "duration_seconds": 10.56
      }
    },
    {
      "id": "bright_female",
      "label": "Bright female",
      "design": {
        "language": "English",
        "text": "The little bookshop was quiet when I arrived. Outside, the rain had stopped, and warm sunlight was finding its way through the windows.",
        "instruct": "A bright adult woman with a light, lively voice, crisp consonants and a curious, smiling conversational tone.",
        "seed": 7302
      },
      "references": {
        "english": {
          "file": "references/bright_female.flac",
          "text": "The little bookshop was quiet when I arrived. Outside, the rain had stopped, and warm sunlight was finding its way through the windows.",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "language": "English",
              "text": "The little bookshop was quiet when I arrived. Outside, the rain had stopped, and warm sunlight was finding its way through the windows.",
              "instruct": "A bright adult woman with a light, lively voice, crisp consonants and a curious, smiling conversational tone.",
              "seed": 7302,
              "mode": "design",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign",
              "non_streaming_mode": true
            },
            "model_revision": "5ecdb67327fd37bb2e042aab12ff7391903235d3",
            "reference_sha256": null
          },
          "fingerprint": "383ce9a9e9b14c185e8c59b35d16e783edfdc51f1462fae1767d6dafc8d11683",
          "sha256": "55d956b1357debc7155a5d818d2c28bec09d75a62e83831630a4997441e56957",
          "bytes": 227489,
          "duration_seconds": 7.68
        },
        "chinese": {
          "file": "references/chinese/bright_female.flac",
          "text": "雨刚停，街道像重新打开的一页纸。 夜里的茶壶很安静，但好像什么都明白。",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "language": "Chinese",
              "text": "雨刚停，街道像重新打开的一页纸。 夜里的茶壶很安静，但好像什么都明白。",
              "instruct": "A bright adult woman with a light, lively voice, crisp consonants and a curious, smiling conversational tone.",
              "seed": 7402,
              "mode": "design",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign",
              "non_streaming_mode": true
            },
            "model_revision": "5ecdb67327fd37bb2e042aab12ff7391903235d3",
            "reference_sha256": null
          },
          "fingerprint": "610a967a3ef15895d7b9d1cf1f9cd10920ed386de328ffcbbe744b629b110d64",
          "sha256": "c01bdddef020b2f3eb1ea5162351ab06288395f8ff245e338f94147a64d29f99",
          "bytes": 211247,
          "duration_seconds": 7.92
        },
        "japanese": {
          "file": "references/japanese/bright_female.flac",
          "text": "雨上がりの道は、新しい一日のページみたいでした。 夕方の風で、街の音が少しやわらぎました。",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "language": "Japanese",
              "text": "雨上がりの道は、新しい一日のページみたいでした。 夕方の風で、街の音が少しやわらぎました。",
              "instruct": "A bright adult woman with a light, lively voice, crisp consonants and a curious, smiling conversational tone.",
              "seed": 7502,
              "mode": "design",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign",
              "non_streaming_mode": true
            },
            "model_revision": "5ecdb67327fd37bb2e042aab12ff7391903235d3",
            "reference_sha256": null
          },
          "fingerprint": "bc5e2218d611a43e41bef59d2f09c688291f2521431511ab23b46136e9ff390c",
          "sha256": "6b7f15fd4025c879578ec154d5943739db23d66393917c99207bf9c626dfc26e",
          "bytes": 251631,
          "duration_seconds": 9.28
        },
        "korean": {
          "file": "references/korean/bright_female.flac",
          "text": "비가 그친 뒤 거리는 새로 시작하는 하루처럼 보였습니다. 저녁 바람이 도시의 소리를 조금 부드럽게 만들었습니다.",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "language": "Korean",
              "text": "비가 그친 뒤 거리는 새로 시작하는 하루처럼 보였습니다. 저녁 바람이 도시의 소리를 조금 부드럽게 만들었습니다.",
              "instruct": "A bright adult woman with a light, lively voice, crisp consonants and a curious, smiling conversational tone.",
              "seed": 7602,
              "mode": "design",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign",
              "non_streaming_mode": true
            },
            "model_revision": "5ecdb67327fd37bb2e042aab12ff7391903235d3",
            "reference_sha256": null
          },
          "fingerprint": "ec275f16857a343218dc7ca24064c0ed52eaf59410d33c335355553dab3149f4",
          "sha256": "6080f008269cd96699b32f26387248166fdaa71f364568bd4f0a46e5f5e80750",
          "bytes": 254182,
          "duration_seconds": 8.32
        },
        "german": {
          "file": "references/german/bright_female.flac",
          "text": "Nach dem Regen sah die Straße aus wie ein neuer Anfang. Der Abendwind machte die Stadt ein wenig freundlicher.",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "language": "German",
              "text": "Nach dem Regen sah die Straße aus wie ein neuer Anfang. Der Abendwind machte die Stadt ein wenig freundlicher.",
              "instruct": "A bright adult woman with a light, lively voice, crisp consonants and a curious, smiling conversational tone.",
              "seed": 7702,
              "mode": "design",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign",
              "non_streaming_mode": true
            },
            "model_revision": "5ecdb67327fd37bb2e042aab12ff7391903235d3",
            "reference_sha256": null
          },
          "fingerprint": "9107d7ac1e2cf9496cbce21e00f2ec4820cc51166465b5c060ec15fd1dee1dc4",
          "sha256": "d5171ddcf4420c8c7703b32a02959f51d900a967d69b628ae202c085e89a1a03",
          "bytes": 194260,
          "duration_seconds": 7.76
        },
        "french": {
          "file": "references/french/bright_female.flac",
          "text": "Après la pluie, la rue semblait recommencer la journée. Le vent du soir a rendu la ville un peu plus douce.",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "language": "French",
              "text": "Après la pluie, la rue semblait recommencer la journée. Le vent du soir a rendu la ville un peu plus douce.",
              "instruct": "A bright adult woman with a light, lively voice, crisp consonants and a curious, smiling conversational tone.",
              "seed": 7802,
              "mode": "design",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign",
              "non_streaming_mode": true
            },
            "model_revision": "5ecdb67327fd37bb2e042aab12ff7391903235d3",
            "reference_sha256": null
          },
          "fingerprint": "5b3ceb5feb26f95f574fe029968f1601358a1c5e29cff70264c5cb7278d72bfc",
          "sha256": "24d68cbc94fb5da76ce0152f99cda901f9b98b70c9af2a293929da919e60aa39",
          "bytes": 184915,
          "duration_seconds": 6.24
        },
        "russian": {
          "file": "references/russian/bright_female.flac",
          "text": "После дождя улица выглядела как новое начало. Вечерний ветер сделал город немного спокойнее.",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "language": "Russian",
              "text": "После дождя улица выглядела как новое начало. Вечерний ветер сделал город немного спокойнее.",
              "instruct": "A bright adult woman with a light, lively voice, crisp consonants and a curious, smiling conversational tone.",
              "seed": 7902,
              "mode": "design",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign",
              "non_streaming_mode": true
            },
            "model_revision": "5ecdb67327fd37bb2e042aab12ff7391903235d3",
            "reference_sha256": null
          },
          "fingerprint": "454636eb5191cddfb9f1c15ad965c62c08ccb80b15832318de35bb85f06fc976",
          "sha256": "b24ad00ecd4c5c79a69f413e24d613e06558d54625373456cd965908bfc77c08",
          "bytes": 220676,
          "duration_seconds": 7.2
        },
        "portuguese": {
          "file": "references/portuguese/bright_female.flac",
          "text": "Depois da chuva, a rua parecia um novo começo. O vento da tarde deixou a cidade um pouco mais calma.",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "language": "Portuguese",
              "text": "Depois da chuva, a rua parecia um novo começo. O vento da tarde deixou a cidade um pouco mais calma.",
              "instruct": "A bright adult woman with a light, lively voice, crisp consonants and a curious, smiling conversational tone.",
              "seed": 8002,
              "mode": "design",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign",
              "non_streaming_mode": true
            },
            "model_revision": "5ecdb67327fd37bb2e042aab12ff7391903235d3",
            "reference_sha256": null
          },
          "fingerprint": "850fd04dd1fb43421622d702a4785067d02540afaf2ca29ac656801151c5372e",
          "sha256": "758b21032a98887f7b6b544c3c30fceaaf6fa102f8912cddcc533265e128620d",
          "bytes": 194178,
          "duration_seconds": 6.64
        },
        "spanish": {
          "file": "references/spanish/bright_female.flac",
          "text": "Después de la lluvia, la calle parecía un nuevo comienzo. El viento de la tarde hizo que la ciudad sonara más tranquila.",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "language": "Spanish",
              "text": "Después de la lluvia, la calle parecía un nuevo comienzo. El viento de la tarde hizo que la ciudad sonara más tranquila.",
              "instruct": "A bright adult woman with a light, lively voice, crisp consonants and a curious, smiling conversational tone.",
              "seed": 8102,
              "mode": "design",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign",
              "non_streaming_mode": true
            },
            "model_revision": "5ecdb67327fd37bb2e042aab12ff7391903235d3",
            "reference_sha256": null
          },
          "fingerprint": "a822aae961e8443f5d3d86687ed8917215352304c2094c544b55b9bdb120c61c",
          "sha256": "7acf060eda868f1ecc12f920d445fab42a4ac0366b3e1501d82ff991b222a9bb",
          "bytes": 275783,
          "duration_seconds": 9.76
        },
        "italian": {
          "file": "references/italian/bright_female.flac",
          "text": "Dopo la pioggia, la strada sembrava un nuovo inizio. Il vento della sera ha reso la città più calma.",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "language": "Italian",
              "text": "Dopo la pioggia, la strada sembrava un nuovo inizio. Il vento della sera ha reso la città più calma.",
              "instruct": "A bright adult woman with a light, lively voice, crisp consonants and a curious, smiling conversational tone.",
              "seed": 8202,
              "mode": "design",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign",
              "non_streaming_mode": true
            },
            "model_revision": "5ecdb67327fd37bb2e042aab12ff7391903235d3",
            "reference_sha256": null
          },
          "fingerprint": "8f6a9ffef18dae7b97ceedc38efd9dd70dfb69cb7c60c133b46217cbb481475b",
          "sha256": "1d9b50f5e09110d7557b96376c9fe1223f6ea74f7a5e0b5f155b7cca39f6bea6",
          "bytes": 168613,
          "duration_seconds": 5.44
        }
      },
      "reference": {
        "file": "references/bright_female.flac",
        "text": "The little bookshop was quiet when I arrived. Outside, the rain had stopped, and warm sunlight was finding its way through the windows.",
        "recipe": {
          "request": {
            "temperature": 0.9,
            "top_k": 50,
            "repetition_penalty": 1.05,
            "max_new_tokens": 600,
            "chunk_size": 8,
            "decoder_context_frames": 25,
            "language": "English",
            "text": "The little bookshop was quiet when I arrived. Outside, the rain had stopped, and warm sunlight was finding its way through the windows.",
            "instruct": "A bright adult woman with a light, lively voice, crisp consonants and a curious, smiling conversational tone.",
            "seed": 7302,
            "mode": "design",
            "model": "Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign",
            "non_streaming_mode": true
          },
          "model_revision": "5ecdb67327fd37bb2e042aab12ff7391903235d3",
          "reference_sha256": null
        },
        "fingerprint": "383ce9a9e9b14c185e8c59b35d16e783edfdc51f1462fae1767d6dafc8d11683",
        "sha256": "55d956b1357debc7155a5d818d2c28bec09d75a62e83831630a4997441e56957",
        "bytes": 227489,
        "duration_seconds": 7.68
      }
    },
    {
      "id": "confident_male",
      "label": "Confident male",
      "design": {
        "language": "English",
        "text": "The little bookshop was quiet when I arrived. Outside, the rain had stopped, and warm sunlight was finding its way through the windows.",
        "instruct": "A confident adult man with a firm middle register, clean articulation and the poised delivery of a documentary presenter.",
        "seed": 7303
      },
      "references": {
        "english": {
          "file": "references/confident_male.flac",
          "text": "The little bookshop was quiet when I arrived. Outside, the rain had stopped, and warm sunlight was finding its way through the windows.",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "language": "English",
              "text": "The little bookshop was quiet when I arrived. Outside, the rain had stopped, and warm sunlight was finding its way through the windows.",
              "instruct": "A confident adult man with a firm middle register, clean articulation and the poised delivery of a documentary presenter.",
              "seed": 7303,
              "mode": "design",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign",
              "non_streaming_mode": true
            },
            "model_revision": "5ecdb67327fd37bb2e042aab12ff7391903235d3",
            "reference_sha256": null
          },
          "fingerprint": "4f39065f7b6604a734f0903bc3b2394108373aa7c9d3157e62637474b05fbcb3",
          "sha256": "107f67576b04f5c0b050327863c198eceb9bab297daf061e4138912595183368",
          "bytes": 207293,
          "duration_seconds": 7.52
        },
        "chinese": {
          "file": "references/chinese/confident_male.flac",
          "text": "雨刚停，街道像重新打开的一页纸。 夜里的茶壶很安静，但好像什么都明白。",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "language": "Chinese",
              "text": "雨刚停，街道像重新打开的一页纸。 夜里的茶壶很安静，但好像什么都明白。",
              "instruct": "A confident adult man with a firm middle register, clean articulation and the poised delivery of a documentary presenter.",
              "seed": 7403,
              "mode": "design",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign",
              "non_streaming_mode": true
            },
            "model_revision": "5ecdb67327fd37bb2e042aab12ff7391903235d3",
            "reference_sha256": null
          },
          "fingerprint": "a876ab6a2285fe6e5e12634755cbb04d0a955fe74c861425a3f7e1322b7d6d7e",
          "sha256": "a726d0fe414eaf607daf1084ba2775323fc724148fb67afe0963a39cbd2e9a07",
          "bytes": 164565,
          "duration_seconds": 6.88
        },
        "japanese": {
          "file": "references/japanese/confident_male.flac",
          "text": "雨上がりの道は、新しい一日のページみたいでした。 夕方の風で、街の音が少しやわらぎました。",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "language": "Japanese",
              "text": "雨上がりの道は、新しい一日のページみたいでした。 夕方の風で、街の音が少しやわらぎました。",
              "instruct": "A confident adult man with a firm middle register, clean articulation and the poised delivery of a documentary presenter.",
              "seed": 7503,
              "mode": "design",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign",
              "non_streaming_mode": true
            },
            "model_revision": "5ecdb67327fd37bb2e042aab12ff7391903235d3",
            "reference_sha256": null
          },
          "fingerprint": "35fbe3e2baba3cde20c45e535ca79d929620c00b81416eb69f59f9573e97f1b5",
          "sha256": "b2b271c5c69ddaa436592dfe7d56b464cf57dff0343b0e79559715c7e72f05b7",
          "bytes": 210778,
          "duration_seconds": 7.44
        },
        "korean": {
          "file": "references/korean/confident_male.flac",
          "text": "비가 그친 뒤 거리는 새로 시작하는 하루처럼 보였습니다. 저녁 바람이 도시의 소리를 조금 부드럽게 만들었습니다.",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "language": "Korean",
              "text": "비가 그친 뒤 거리는 새로 시작하는 하루처럼 보였습니다. 저녁 바람이 도시의 소리를 조금 부드럽게 만들었습니다.",
              "instruct": "A confident adult man with a firm middle register, clean articulation and the poised delivery of a documentary presenter.",
              "seed": 7603,
              "mode": "design",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign",
              "non_streaming_mode": true
            },
            "model_revision": "5ecdb67327fd37bb2e042aab12ff7391903235d3",
            "reference_sha256": null
          },
          "fingerprint": "517fd7dc14c5caceb10409cebc1d81b8a7a01747c8fba6718962894d6ba7a53e",
          "sha256": "abb5934d20218e2670421316207e4cb9e35c80c0d039c55043c6bbb77c26090c",
          "bytes": 239871,
          "duration_seconds": 7.92
        },
        "german": {
          "file": "references/german/confident_male.flac",
          "text": "Nach dem Regen sah die Straße aus wie ein neuer Anfang. Der Abendwind machte die Stadt ein wenig freundlicher.",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "language": "German",
              "text": "Nach dem Regen sah die Straße aus wie ein neuer Anfang. Der Abendwind machte die Stadt ein wenig freundlicher.",
              "instruct": "A confident adult man with a firm middle register, clean articulation and the poised delivery of a documentary presenter.",
              "seed": 7703,
              "mode": "design",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign",
              "non_streaming_mode": true
            },
            "model_revision": "5ecdb67327fd37bb2e042aab12ff7391903235d3",
            "reference_sha256": null
          },
          "fingerprint": "c392fd139407a384e71176cc9cd2c5f0f2ee99448bb4266a89bdd45305bb98de",
          "sha256": "d57bcf128cf022cdea552927c876c1f283aa3559cf496bf733375c619be7b9b3",
          "bytes": 196030,
          "duration_seconds": 7.6
        },
        "french": {
          "file": "references/french/confident_male.flac",
          "text": "Après la pluie, la rue semblait recommencer la journée. Le vent du soir a rendu la ville un peu plus douce.",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "language": "French",
              "text": "Après la pluie, la rue semblait recommencer la journée. Le vent du soir a rendu la ville un peu plus douce.",
              "instruct": "A confident adult man with a firm middle register, clean articulation and the poised delivery of a documentary presenter.",
              "seed": 7803,
              "mode": "design",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign",
              "non_streaming_mode": true
            },
            "model_revision": "5ecdb67327fd37bb2e042aab12ff7391903235d3",
            "reference_sha256": null
          },
          "fingerprint": "30e48c03b907435a53931e11f4edb98fd94b2113807228a7ff019f5279fba429",
          "sha256": "86cc41f057f27dca6956698379c2c7c2da2e77e5aa60c82a1f100a3fc7492024",
          "bytes": 186188,
          "duration_seconds": 6.72
        },
        "russian": {
          "file": "references/russian/confident_male.flac",
          "text": "После дождя улица выглядела как новое начало. Вечерний ветер сделал город немного спокойнее.",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "language": "Russian",
              "text": "После дождя улица выглядела как новое начало. Вечерний ветер сделал город немного спокойнее.",
              "instruct": "A confident adult man with a firm middle register, clean articulation and the poised delivery of a documentary presenter.",
              "seed": 7903,
              "mode": "design",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign",
              "non_streaming_mode": true
            },
            "model_revision": "5ecdb67327fd37bb2e042aab12ff7391903235d3",
            "reference_sha256": null
          },
          "fingerprint": "71f841734279f8bc0419fe187b5d78527f0c928f92a35dc131f83a79781fd4f9",
          "sha256": "2f18f8cfebfeb5ec2f48141b942a357c62bcad1436ad9a1338194a95af383ff8",
          "bytes": 200030,
          "duration_seconds": 6.48
        },
        "portuguese": {
          "file": "references/portuguese/confident_male.flac",
          "text": "Depois da chuva, a rua parecia um novo começo. O vento da tarde deixou a cidade um pouco mais calma.",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "language": "Portuguese",
              "text": "Depois da chuva, a rua parecia um novo começo. O vento da tarde deixou a cidade um pouco mais calma.",
              "instruct": "A confident adult man with a firm middle register, clean articulation and the poised delivery of a documentary presenter.",
              "seed": 8003,
              "mode": "design",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign",
              "non_streaming_mode": true
            },
            "model_revision": "5ecdb67327fd37bb2e042aab12ff7391903235d3",
            "reference_sha256": null
          },
          "fingerprint": "f00ca0e251648f5f699e07d594ad58406419c413833849d1cba1bbc2ef4f1681",
          "sha256": "e0b5cdf177a132ceb477c9e474ea70fa6626c39672bc27d20f5653f62110a1ba",
          "bytes": 183818,
          "duration_seconds": 6.8
        },
        "spanish": {
          "file": "references/spanish/confident_male.flac",
          "text": "Después de la lluvia, la calle parecía un nuevo comienzo. El viento de la tarde hizo que la ciudad sonara más tranquila.",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "language": "Spanish",
              "text": "Después de la lluvia, la calle parecía un nuevo comienzo. El viento de la tarde hizo que la ciudad sonara más tranquila.",
              "instruct": "A confident adult man with a firm middle register, clean articulation and the poised delivery of a documentary presenter.",
              "seed": 8103,
              "mode": "design",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign",
              "non_streaming_mode": true
            },
            "model_revision": "5ecdb67327fd37bb2e042aab12ff7391903235d3",
            "reference_sha256": null
          },
          "fingerprint": "0e827b5c6d718bdb0c234570a2edd9bc56922466db904b4afa106de5f7fe90d2",
          "sha256": "f3e01046bd4ce834bc2aee3c5a53cac7ef6d27efecbdb4413a965eb3bab5203b",
          "bytes": 221128,
          "duration_seconds": 7.84
        },
        "italian": {
          "file": "references/italian/confident_male.flac",
          "text": "Dopo la pioggia, la strada sembrava un nuovo inizio. Il vento della sera ha reso la città più calma.",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "language": "Italian",
              "text": "Dopo la pioggia, la strada sembrava un nuovo inizio. Il vento della sera ha reso la città più calma.",
              "instruct": "A confident adult man with a firm middle register, clean articulation and the poised delivery of a documentary presenter.",
              "seed": 8203,
              "mode": "design",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign",
              "non_streaming_mode": true
            },
            "model_revision": "5ecdb67327fd37bb2e042aab12ff7391903235d3",
            "reference_sha256": null
          },
          "fingerprint": "04244279c05d78de148a64fa121c334f20127324cca9e484e7c86b04d418f7b2",
          "sha256": "ba1d9120594f46f3295f5bf1a9327dbdc79fd5b79065e36922be75b5605dd12b",
          "bytes": 183238,
          "duration_seconds": 6.32
        }
      },
      "reference": {
        "file": "references/confident_male.flac",
        "text": "The little bookshop was quiet when I arrived. Outside, the rain had stopped, and warm sunlight was finding its way through the windows.",
        "recipe": {
          "request": {
            "temperature": 0.9,
            "top_k": 50,
            "repetition_penalty": 1.05,
            "max_new_tokens": 600,
            "chunk_size": 8,
            "decoder_context_frames": 25,
            "language": "English",
            "text": "The little bookshop was quiet when I arrived. Outside, the rain had stopped, and warm sunlight was finding its way through the windows.",
            "instruct": "A confident adult man with a firm middle register, clean articulation and the poised delivery of a documentary presenter.",
            "seed": 7303,
            "mode": "design",
            "model": "Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign",
            "non_streaming_mode": true
          },
          "model_revision": "5ecdb67327fd37bb2e042aab12ff7391903235d3",
          "reference_sha256": null
        },
        "fingerprint": "4f39065f7b6604a734f0903bc3b2394108373aa7c9d3157e62637474b05fbcb3",
        "sha256": "107f67576b04f5c0b050327863c198eceb9bab297daf061e4138912595183368",
        "bytes": 207293,
        "duration_seconds": 7.52
      }
    },
    {
      "id": "gentle_female",
      "label": "Gentle female",
      "design": {
        "language": "English",
        "text": "The little bookshop was quiet when I arrived. Outside, the rain had stopped, and warm sunlight was finding its way through the windows.",
        "instruct": "A gentle adult woman with a soft low voice, intimate close-microphone warmth and a relaxed, comforting cadence.",
        "seed": 7304
      },
      "references": {
        "english": {
          "file": "references/gentle_female.flac",
          "text": "The little bookshop was quiet when I arrived. Outside, the rain had stopped, and warm sunlight was finding its way through the windows.",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "language": "English",
              "text": "The little bookshop was quiet when I arrived. Outside, the rain had stopped, and warm sunlight was finding its way through the windows.",
              "instruct": "A gentle adult woman with a soft low voice, intimate close-microphone warmth and a relaxed, comforting cadence.",
              "seed": 7304,
              "mode": "design",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign",
              "non_streaming_mode": true
            },
            "model_revision": "5ecdb67327fd37bb2e042aab12ff7391903235d3",
            "reference_sha256": null
          },
          "fingerprint": "e1b03f401b21bbbbde27eabd3093ab60fe6a0cdf66056bbcfe80e0d1c5ad8a5a",
          "sha256": "2ecedbfcc33cb3336eb218771fafaf86c5de81282162a54322658eb6df33ff54",
          "bytes": 246625,
          "duration_seconds": 9.2
        },
        "chinese": {
          "file": "references/chinese/gentle_female.flac",
          "text": "雨刚停，街道像重新打开的一页纸。 夜里的茶壶很安静，但好像什么都明白。",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "language": "Chinese",
              "text": "雨刚停，街道像重新打开的一页纸。 夜里的茶壶很安静，但好像什么都明白。",
              "instruct": "A gentle adult woman with a soft low voice, intimate close-microphone warmth and a relaxed, comforting cadence.",
              "seed": 7404,
              "mode": "design",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign",
              "non_streaming_mode": true
            },
            "model_revision": "5ecdb67327fd37bb2e042aab12ff7391903235d3",
            "reference_sha256": null
          },
          "fingerprint": "b86b1307c61bf4e23dceba35d74de1cc3b71f0f037c9a38e6600841702e17c91",
          "sha256": "36480b8c4fa53b1737151dc2df6c959d83b3a3e10560b447a794b446a960647a",
          "bytes": 220594,
          "duration_seconds": 8.08
        },
        "japanese": {
          "file": "references/japanese/gentle_female.flac",
          "text": "雨上がりの道は、新しい一日のページみたいでした。 夕方の風で、街の音が少しやわらぎました。",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "language": "Japanese",
              "text": "雨上がりの道は、新しい一日のページみたいでした。 夕方の風で、街の音が少しやわらぎました。",
              "instruct": "A gentle adult woman with a soft low voice, intimate close-microphone warmth and a relaxed, comforting cadence.",
              "seed": 7504,
              "mode": "design",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign",
              "non_streaming_mode": true
            },
            "model_revision": "5ecdb67327fd37bb2e042aab12ff7391903235d3",
            "reference_sha256": null
          },
          "fingerprint": "8795739146eeba1105f2cddf649d8cc4e891c13653f1c5b2a2c7e1ac543938e0",
          "sha256": "fbdd730ccb29438ab1e14cb848dcda1a89d6deb84144715ce42e19da475ffc5e",
          "bytes": 266989,
          "duration_seconds": 9.84
        },
        "korean": {
          "file": "references/korean/gentle_female.flac",
          "text": "비가 그친 뒤 거리는 새로 시작하는 하루처럼 보였습니다. 저녁 바람이 도시의 소리를 조금 부드럽게 만들었습니다.",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "language": "Korean",
              "text": "비가 그친 뒤 거리는 새로 시작하는 하루처럼 보였습니다. 저녁 바람이 도시의 소리를 조금 부드럽게 만들었습니다.",
              "instruct": "A gentle adult woman with a soft low voice, intimate close-microphone warmth and a relaxed, comforting cadence.",
              "seed": 7604,
              "mode": "design",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign",
              "non_streaming_mode": true
            },
            "model_revision": "5ecdb67327fd37bb2e042aab12ff7391903235d3",
            "reference_sha256": null
          },
          "fingerprint": "d359d8ed1e2bbc6d4319d6ef6672a3f2bc8239554f537f13a4f5ca7956a69f28",
          "sha256": "deb07ad7edecf6b88f03ac6ce20bf0892d2596cdd6c53f10a39a74c1b4ed3d00",
          "bytes": 265356,
          "duration_seconds": 9.92
        },
        "german": {
          "file": "references/german/gentle_female.flac",
          "text": "Nach dem Regen sah die Straße aus wie ein neuer Anfang. Der Abendwind machte die Stadt ein wenig freundlicher.",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "language": "German",
              "text": "Nach dem Regen sah die Straße aus wie ein neuer Anfang. Der Abendwind machte die Stadt ein wenig freundlicher.",
              "instruct": "A gentle adult woman with a soft low voice, intimate close-microphone warmth and a relaxed, comforting cadence.",
              "seed": 7704,
              "mode": "design",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign",
              "non_streaming_mode": true
            },
            "model_revision": "5ecdb67327fd37bb2e042aab12ff7391903235d3",
            "reference_sha256": null
          },
          "fingerprint": "fb1c52e81ea805778e7ecc4514b4608e18a8fadd4f1c934f117c027f31bd3f68",
          "sha256": "fe76a572a92edf07b88e19be7080fb95a18eccf79ad191745936b970048e07b6",
          "bytes": 188886,
          "duration_seconds": 7.52
        },
        "french": {
          "file": "references/french/gentle_female.flac",
          "text": "Après la pluie, la rue semblait recommencer la journée. Le vent du soir a rendu la ville un peu plus douce.",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "language": "French",
              "text": "Après la pluie, la rue semblait recommencer la journée. Le vent du soir a rendu la ville un peu plus douce.",
              "instruct": "A gentle adult woman with a soft low voice, intimate close-microphone warmth and a relaxed, comforting cadence.",
              "seed": 7804,
              "mode": "design",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign",
              "non_streaming_mode": true
            },
            "model_revision": "5ecdb67327fd37bb2e042aab12ff7391903235d3",
            "reference_sha256": null
          },
          "fingerprint": "fe2ddfb109a2a9867950f9479fad92482771b8799632dab66efb4162f0303f6c",
          "sha256": "28ece923b32fe38b858ce4a01faf80c81ad15f31d5edba0aab2364c11a7d1aa1",
          "bytes": 182383,
          "duration_seconds": 6.64
        },
        "russian": {
          "file": "references/russian/gentle_female.flac",
          "text": "После дождя улица выглядела как новое начало. Вечерний ветер сделал город немного спокойнее.",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "language": "Russian",
              "text": "После дождя улица выглядела как новое начало. Вечерний ветер сделал город немного спокойнее.",
              "instruct": "A gentle adult woman with a soft low voice, intimate close-microphone warmth and a relaxed, comforting cadence.",
              "seed": 7904,
              "mode": "design",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign",
              "non_streaming_mode": true
            },
            "model_revision": "5ecdb67327fd37bb2e042aab12ff7391903235d3",
            "reference_sha256": null
          },
          "fingerprint": "0698b30bea5a454947aa2983ad5bd9eb0a7677b32a268eb0ea70755ffae6d747",
          "sha256": "28904b9956b7b318f31ac7617a40c7f2b527f0960b2cb989a6b861ccf3d64086",
          "bytes": 204000,
          "duration_seconds": 7.04
        },
        "portuguese": {
          "file": "references/portuguese/gentle_female.flac",
          "text": "Depois da chuva, a rua parecia um novo começo. O vento da tarde deixou a cidade um pouco mais calma.",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "language": "Portuguese",
              "text": "Depois da chuva, a rua parecia um novo começo. O vento da tarde deixou a cidade um pouco mais calma.",
              "instruct": "A gentle adult woman with a soft low voice, intimate close-microphone warmth and a relaxed, comforting cadence.",
              "seed": 8004,
              "mode": "design",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign",
              "non_streaming_mode": true
            },
            "model_revision": "5ecdb67327fd37bb2e042aab12ff7391903235d3",
            "reference_sha256": null
          },
          "fingerprint": "c3b2dc66c2fc69f5f66e9af69f68685aee42600a51531bf26289be40d7779310",
          "sha256": "4f43eb6f29ece903df78b959c90d73405d5fa3583ca9329aaceca720097ec35c",
          "bytes": 227868,
          "duration_seconds": 8.4
        },
        "spanish": {
          "file": "references/spanish/gentle_female.flac",
          "text": "Después de la lluvia, la calle parecía un nuevo comienzo. El viento de la tarde hizo que la ciudad sonara más tranquila.",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "language": "Spanish",
              "text": "Después de la lluvia, la calle parecía un nuevo comienzo. El viento de la tarde hizo que la ciudad sonara más tranquila.",
              "instruct": "A gentle adult woman with a soft low voice, intimate close-microphone warmth and a relaxed, comforting cadence.",
              "seed": 8104,
              "mode": "design",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign",
              "non_streaming_mode": true
            },
            "model_revision": "5ecdb67327fd37bb2e042aab12ff7391903235d3",
            "reference_sha256": null
          },
          "fingerprint": "598764da0138bb91a116edb8917b6e87653ad5f848e2d0db435bab1f45565936",
          "sha256": "89a2b3a75efce83d508c1b5906cb9f77a67953058df32a3b06e07c017d044d07",
          "bytes": 281676,
          "duration_seconds": 11.12
        },
        "italian": {
          "file": "references/italian/gentle_female.flac",
          "text": "Dopo la pioggia, la strada sembrava un nuovo inizio. Il vento della sera ha reso la città più calma.",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "language": "Italian",
              "text": "Dopo la pioggia, la strada sembrava un nuovo inizio. Il vento della sera ha reso la città più calma.",
              "instruct": "A gentle adult woman with a soft low voice, intimate close-microphone warmth and a relaxed, comforting cadence.",
              "seed": 8204,
              "mode": "design",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign",
              "non_streaming_mode": true
            },
            "model_revision": "5ecdb67327fd37bb2e042aab12ff7391903235d3",
            "reference_sha256": null
          },
          "fingerprint": "cfb5e7a9563d5a2f5cdee70758fed534fb82c927e21568147e1f5eaf5e814a65",
          "sha256": "e6e8c20d0c5c1a94ad6aab78b495766c44db462c60481cb4d6e85c8d3c893b6a",
          "bytes": 184778,
          "duration_seconds": 6.56
        }
      },
      "reference": {
        "file": "references/gentle_female.flac",
        "text": "The little bookshop was quiet when I arrived. Outside, the rain had stopped, and warm sunlight was finding its way through the windows.",
        "recipe": {
          "request": {
            "temperature": 0.9,
            "top_k": 50,
            "repetition_penalty": 1.05,
            "max_new_tokens": 600,
            "chunk_size": 8,
            "decoder_context_frames": 25,
            "language": "English",
            "text": "The little bookshop was quiet when I arrived. Outside, the rain had stopped, and warm sunlight was finding its way through the windows.",
            "instruct": "A gentle adult woman with a soft low voice, intimate close-microphone warmth and a relaxed, comforting cadence.",
            "seed": 7304,
            "mode": "design",
            "model": "Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign",
            "non_streaming_mode": true
          },
          "model_revision": "5ecdb67327fd37bb2e042aab12ff7391903235d3",
          "reference_sha256": null
        },
        "fingerprint": "e1b03f401b21bbbbde27eabd3093ab60fe6a0cdf66056bbcfe80e0d1c5ad8a5a",
        "sha256": "2ecedbfcc33cb3336eb218771fafaf86c5de81282162a54322658eb6df33ff54",
        "bytes": 246625,
        "duration_seconds": 9.2
      }
    },
    {
      "id": "clear_male",
      "label": "Clear male",
      "design": {
        "language": "English",
        "text": "The little bookshop was quiet when I arrived. Outside, the rain had stopped, and warm sunlight was finding its way through the windows.",
        "instruct": "An adult man with a clear tenor voice, precise diction and an engaged, friendly educational presentation style.",
        "seed": 7305
      },
      "references": {
        "english": {
          "file": "references/clear_male.flac",
          "text": "The little bookshop was quiet when I arrived. Outside, the rain had stopped, and warm sunlight was finding its way through the windows.",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "language": "English",
              "text": "The little bookshop was quiet when I arrived. Outside, the rain had stopped, and warm sunlight was finding its way through the windows.",
              "instruct": "An adult man with a clear tenor voice, precise diction and an engaged, friendly educational presentation style.",
              "seed": 7305,
              "mode": "design",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign",
              "non_streaming_mode": true
            },
            "model_revision": "5ecdb67327fd37bb2e042aab12ff7391903235d3",
            "reference_sha256": null
          },
          "fingerprint": "71c85e3bf4c6acbaa5abc7eb2cda54c1a7c8885192db579a18eabc2b00a41f7b",
          "sha256": "fdc6ccb085e5635ec60ae06463d4f7002d67461521969816f192ac4989dc36b7",
          "bytes": 230366,
          "duration_seconds": 8.32
        },
        "chinese": {
          "file": "references/chinese/clear_male.flac",
          "text": "雨刚停，街道像重新打开的一页纸。 夜里的茶壶很安静，但好像什么都明白。",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "language": "Chinese",
              "text": "雨刚停，街道像重新打开的一页纸。 夜里的茶壶很安静，但好像什么都明白。",
              "instruct": "An adult man with a clear tenor voice, precise diction and an engaged, friendly educational presentation style.",
              "seed": 7405,
              "mode": "design",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign",
              "non_streaming_mode": true
            },
            "model_revision": "5ecdb67327fd37bb2e042aab12ff7391903235d3",
            "reference_sha256": null
          },
          "fingerprint": "12ba31f997077ff12986d743b3535efaa5aacac42afb8b529a67f2031c0c50c4",
          "sha256": "193c397818e74f27fbe5090b6b4d087fc4d3b90db205180741b0bf9f0b373bde",
          "bytes": 167894,
          "duration_seconds": 6.56
        },
        "japanese": {
          "file": "references/japanese/clear_male.flac",
          "text": "雨上がりの道は、新しい一日のページみたいでした。 夕方の風で、街の音が少しやわらぎました。",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "language": "Japanese",
              "text": "雨上がりの道は、新しい一日のページみたいでした。 夕方の風で、街の音が少しやわらぎました。",
              "instruct": "An adult man with a clear tenor voice, precise diction and an engaged, friendly educational presentation style.",
              "seed": 7505,
              "mode": "design",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign",
              "non_streaming_mode": true
            },
            "model_revision": "5ecdb67327fd37bb2e042aab12ff7391903235d3",
            "reference_sha256": null
          },
          "fingerprint": "9667f7ade2aa025da667d64397a85c6ffcc37a952730076fb48b67a759469a9b",
          "sha256": "26f2b9b45f535c430e001191d9c483a01200708e1c0e83cb20705fe50a7cdc6d",
          "bytes": 228371,
          "duration_seconds": 8.0
        },
        "korean": {
          "file": "references/korean/clear_male.flac",
          "text": "비가 그친 뒤 거리는 새로 시작하는 하루처럼 보였습니다. 저녁 바람이 도시의 소리를 조금 부드럽게 만들었습니다.",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "language": "Korean",
              "text": "비가 그친 뒤 거리는 새로 시작하는 하루처럼 보였습니다. 저녁 바람이 도시의 소리를 조금 부드럽게 만들었습니다.",
              "instruct": "An adult man with a clear tenor voice, precise diction and an engaged, friendly educational presentation style.",
              "seed": 7605,
              "mode": "design",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign",
              "non_streaming_mode": true
            },
            "model_revision": "5ecdb67327fd37bb2e042aab12ff7391903235d3",
            "reference_sha256": null
          },
          "fingerprint": "0a8ebe2feab9b62b4b9c9102963ed0fb0819319e11b3955e46f81ce8fda7e720",
          "sha256": "299820179a682766cf1a767e8c5cffdcc02f7df853b409a70095a0c2889da51b",
          "bytes": 204888,
          "duration_seconds": 7.92
        },
        "german": {
          "file": "references/german/clear_male.flac",
          "text": "Nach dem Regen sah die Straße aus wie ein neuer Anfang. Der Abendwind machte die Stadt ein wenig freundlicher.",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "language": "German",
              "text": "Nach dem Regen sah die Straße aus wie ein neuer Anfang. Der Abendwind machte die Stadt ein wenig freundlicher.",
              "instruct": "An adult man with a clear tenor voice, precise diction and an engaged, friendly educational presentation style.",
              "seed": 7705,
              "mode": "design",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign",
              "non_streaming_mode": true
            },
            "model_revision": "5ecdb67327fd37bb2e042aab12ff7391903235d3",
            "reference_sha256": null
          },
          "fingerprint": "7f4d69ebf6a52686a2e163f4b5bfc7ec8cbb12c748d88fa93cd9429361e2b01b",
          "sha256": "beb7c0d5bddf0cb5576a1578a5724e1fce39dac42e6c164c84a8021a8d682883",
          "bytes": 183960,
          "duration_seconds": 6.56
        },
        "french": {
          "file": "references/french/clear_male.flac",
          "text": "Après la pluie, la rue semblait recommencer la journée. Le vent du soir a rendu la ville un peu plus douce.",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "language": "French",
              "text": "Après la pluie, la rue semblait recommencer la journée. Le vent du soir a rendu la ville un peu plus douce.",
              "instruct": "An adult man with a clear tenor voice, precise diction and an engaged, friendly educational presentation style.",
              "seed": 7805,
              "mode": "design",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign",
              "non_streaming_mode": true
            },
            "model_revision": "5ecdb67327fd37bb2e042aab12ff7391903235d3",
            "reference_sha256": null
          },
          "fingerprint": "fb87bdbe421f3b210eb7fbec070f80138fee4d9d298d1fb13cbabf457206ede8",
          "sha256": "60ac7aa7f0346b9deef86e8bf990e1aa83be3b600b0b108915bf1b46d52ff490",
          "bytes": 178155,
          "duration_seconds": 5.84
        },
        "russian": {
          "file": "references/russian/clear_male.flac",
          "text": "После дождя улица выглядела как новое начало. Вечерний ветер сделал город немного спокойнее.",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "language": "Russian",
              "text": "После дождя улица выглядела как новое начало. Вечерний ветер сделал город немного спокойнее.",
              "instruct": "An adult man with a clear tenor voice, precise diction and an engaged, friendly educational presentation style.",
              "seed": 7905,
              "mode": "design",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign",
              "non_streaming_mode": true
            },
            "model_revision": "5ecdb67327fd37bb2e042aab12ff7391903235d3",
            "reference_sha256": null
          },
          "fingerprint": "78ccace81cfb78b854b12fd53c551ca48abe45f2cf6fd70a8aaf5e7ba2dfbbd3",
          "sha256": "e896a56ed3696a67fc491120da5284daff20830aecbc417e470136e19535a044",
          "bytes": 196165,
          "duration_seconds": 6.56
        },
        "portuguese": {
          "file": "references/portuguese/clear_male.flac",
          "text": "Depois da chuva, a rua parecia um novo começo. O vento da tarde deixou a cidade um pouco mais calma.",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "language": "Portuguese",
              "text": "Depois da chuva, a rua parecia um novo começo. O vento da tarde deixou a cidade um pouco mais calma.",
              "instruct": "An adult man with a clear tenor voice, precise diction and an engaged, friendly educational presentation style.",
              "seed": 8005,
              "mode": "design",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign",
              "non_streaming_mode": true
            },
            "model_revision": "5ecdb67327fd37bb2e042aab12ff7391903235d3",
            "reference_sha256": null
          },
          "fingerprint": "df424a180689a27e2e6b1e48da116960b8c4e554bd8ffcb1fc1e32b866e4c950",
          "sha256": "47bd8f606bb8de073b916f39c69d97ca7b667a2fcf8fa3368d89690768ac1080",
          "bytes": 173559,
          "duration_seconds": 6.24
        },
        "spanish": {
          "file": "references/spanish/clear_male.flac",
          "text": "Después de la lluvia, la calle parecía un nuevo comienzo. El viento de la tarde hizo que la ciudad sonara más tranquila.",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "language": "Spanish",
              "text": "Después de la lluvia, la calle parecía un nuevo comienzo. El viento de la tarde hizo que la ciudad sonara más tranquila.",
              "instruct": "An adult man with a clear tenor voice, precise diction and an engaged, friendly educational presentation style.",
              "seed": 8105,
              "mode": "design",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign",
              "non_streaming_mode": true
            },
            "model_revision": "5ecdb67327fd37bb2e042aab12ff7391903235d3",
            "reference_sha256": null
          },
          "fingerprint": "00d0540ad825ee6696d35bb71b1e427ce4ef5c7c52905d5a3981d318d488bbb2",
          "sha256": "65f341028c31e27a2493c787bd722d3d9d1648bacd26604affe06734a9d90ec3",
          "bytes": 244673,
          "duration_seconds": 8.4
        },
        "italian": {
          "file": "references/italian/clear_male.flac",
          "text": "Dopo la pioggia, la strada sembrava un nuovo inizio. Il vento della sera ha reso la città più calma.",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "language": "Italian",
              "text": "Dopo la pioggia, la strada sembrava un nuovo inizio. Il vento della sera ha reso la città più calma.",
              "instruct": "An adult man with a clear tenor voice, precise diction and an engaged, friendly educational presentation style.",
              "seed": 8205,
              "mode": "design",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign",
              "non_streaming_mode": true
            },
            "model_revision": "5ecdb67327fd37bb2e042aab12ff7391903235d3",
            "reference_sha256": null
          },
          "fingerprint": "c1551e11cdc7710690ce83f623373fee9bc49d04a3ffa4208efdc3b86c8624e5",
          "sha256": "00e14348771f0fa77ffa8f3ff2ec782cbf362466e4de2ea4f8c4f8a3cde622a0",
          "bytes": 160968,
          "duration_seconds": 5.92
        }
      },
      "reference": {
        "file": "references/clear_male.flac",
        "text": "The little bookshop was quiet when I arrived. Outside, the rain had stopped, and warm sunlight was finding its way through the windows.",
        "recipe": {
          "request": {
            "temperature": 0.9,
            "top_k": 50,
            "repetition_penalty": 1.05,
            "max_new_tokens": 600,
            "chunk_size": 8,
            "decoder_context_frames": 25,
            "language": "English",
            "text": "The little bookshop was quiet when I arrived. Outside, the rain had stopped, and warm sunlight was finding its way through the windows.",
            "instruct": "An adult man with a clear tenor voice, precise diction and an engaged, friendly educational presentation style.",
            "seed": 7305,
            "mode": "design",
            "model": "Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign",
            "non_streaming_mode": true
          },
          "model_revision": "5ecdb67327fd37bb2e042aab12ff7391903235d3",
          "reference_sha256": null
        },
        "fingerprint": "71c85e3bf4c6acbaa5abc7eb2cda54c1a7c8885192db579a18eabc2b00a41f7b",
        "sha256": "fdc6ccb085e5635ec60ae06463d4f7002d67461521969816f192ac4989dc36b7",
        "bytes": 230366,
        "duration_seconds": 8.32
      }
    },
    {
      "id": "relaxed_female",
      "label": "Relaxed female",
      "design": {
        "language": "English",
        "text": "The little bookshop was quiet when I arrived. Outside, the rain had stopped, and warm sunlight was finding its way through the windows.",
        "instruct": "An adult woman with a mellow, slightly husky voice and an easy, natural conversational rhythm.",
        "seed": 7306
      },
      "references": {
        "english": {
          "file": "references/relaxed_female.flac",
          "text": "The little bookshop was quiet when I arrived. Outside, the rain had stopped, and warm sunlight was finding its way through the windows.",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "language": "English",
              "text": "The little bookshop was quiet when I arrived. Outside, the rain had stopped, and warm sunlight was finding its way through the windows.",
              "instruct": "An adult woman with a mellow, slightly husky voice and an easy, natural conversational rhythm.",
              "seed": 7306,
              "mode": "design",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign",
              "non_streaming_mode": true
            },
            "model_revision": "5ecdb67327fd37bb2e042aab12ff7391903235d3",
            "reference_sha256": null
          },
          "fingerprint": "6f2db0cb659b3efa6996949b2850d4c3fb7513548a5c8859ce259ff8e3c64b07",
          "sha256": "be45cd88d025d50a546f244603f1787668b357000709f6ec45b395cd6070b0a5",
          "bytes": 237141,
          "duration_seconds": 9.2
        },
        "chinese": {
          "file": "references/chinese/relaxed_female.flac",
          "text": "雨刚停，街道像重新打开的一页纸。 夜里的茶壶很安静，但好像什么都明白。",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "language": "Chinese",
              "text": "雨刚停，街道像重新打开的一页纸。 夜里的茶壶很安静，但好像什么都明白。",
              "instruct": "An adult woman with a mellow, slightly husky voice and an easy, natural conversational rhythm.",
              "seed": 7406,
              "mode": "design",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign",
              "non_streaming_mode": true
            },
            "model_revision": "5ecdb67327fd37bb2e042aab12ff7391903235d3",
            "reference_sha256": null
          },
          "fingerprint": "ab27d7263f731ce8c281e168338eb85d8e86b2e13ad4463f1305aefb08a8567e",
          "sha256": "6d7c98a25d71fcb90ba2d6578f0108d7995016d326ffb1fbac56b2a0db0a0a07",
          "bytes": 196005,
          "duration_seconds": 8.0
        },
        "japanese": {
          "file": "references/japanese/relaxed_female.flac",
          "text": "雨上がりの道は、新しい一日のページみたいでした。 夕方の風で、街の音が少しやわらぎました。",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "language": "Japanese",
              "text": "雨上がりの道は、新しい一日のページみたいでした。 夕方の風で、街の音が少しやわらぎました。",
              "instruct": "An adult woman with a mellow, slightly husky voice and an easy, natural conversational rhythm.",
              "seed": 7506,
              "mode": "design",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign",
              "non_streaming_mode": true
            },
            "model_revision": "5ecdb67327fd37bb2e042aab12ff7391903235d3",
            "reference_sha256": null
          },
          "fingerprint": "1fceb1c6d2c3ff1e8df9e50441ffc30d28bb76a9046db1c33038a16243f046d3",
          "sha256": "5e783cf091a8153c2d3c3de6551d005cfc38c3683ef2a7444143463f73667fa0",
          "bytes": 271215,
          "duration_seconds": 10.0
        },
        "korean": {
          "file": "references/korean/relaxed_female.flac",
          "text": "비가 그친 뒤 거리는 새로 시작하는 하루처럼 보였습니다. 저녁 바람이 도시의 소리를 조금 부드럽게 만들었습니다.",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "language": "Korean",
              "text": "비가 그친 뒤 거리는 새로 시작하는 하루처럼 보였습니다. 저녁 바람이 도시의 소리를 조금 부드럽게 만들었습니다.",
              "instruct": "An adult woman with a mellow, slightly husky voice and an easy, natural conversational rhythm.",
              "seed": 7606,
              "mode": "design",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign",
              "non_streaming_mode": true
            },
            "model_revision": "5ecdb67327fd37bb2e042aab12ff7391903235d3",
            "reference_sha256": null
          },
          "fingerprint": "298f97beeab1d71f4df4ad5a5790b3a3d4830b2cc488309c75c0e85d05425b77",
          "sha256": "7ce1df486a113bf47365d73cc1ce166d5f696fedb9843ac56614b82b281a1c9f",
          "bytes": 275990,
          "duration_seconds": 10.56
        },
        "german": {
          "file": "references/german/relaxed_female.flac",
          "text": "Nach dem Regen sah die Straße aus wie ein neuer Anfang. Der Abendwind machte die Stadt ein wenig freundlicher.",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "language": "German",
              "text": "Nach dem Regen sah die Straße aus wie ein neuer Anfang. Der Abendwind machte die Stadt ein wenig freundlicher.",
              "instruct": "An adult woman with a mellow, slightly husky voice and an easy, natural conversational rhythm.",
              "seed": 7706,
              "mode": "design",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign",
              "non_streaming_mode": true
            },
            "model_revision": "5ecdb67327fd37bb2e042aab12ff7391903235d3",
            "reference_sha256": null
          },
          "fingerprint": "838a405707eb0d152de8a708ed9ca217ccbc4918e644891266172be901d8075e",
          "sha256": "a3a94457c71b58c8648d1ead384b746b3847082c40ca6609430f18585d02d5a8",
          "bytes": 172368,
          "duration_seconds": 6.08
        },
        "french": {
          "file": "references/french/relaxed_female.flac",
          "text": "Après la pluie, la rue semblait recommencer la journée. Le vent du soir a rendu la ville un peu plus douce.",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "language": "French",
              "text": "Après la pluie, la rue semblait recommencer la journée. Le vent du soir a rendu la ville un peu plus douce.",
              "instruct": "An adult woman with a mellow, slightly husky voice and an easy, natural conversational rhythm.",
              "seed": 7806,
              "mode": "design",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign",
              "non_streaming_mode": true
            },
            "model_revision": "5ecdb67327fd37bb2e042aab12ff7391903235d3",
            "reference_sha256": null
          },
          "fingerprint": "8ad06fa01838517bd18f80828b864567fd55df2df783521b49eba7d6cb726e04",
          "sha256": "2b0e8b8b3863c7655a83651dd9ec47b1de4bf79774ce1bd8b100b80574c9ae81",
          "bytes": 196911,
          "duration_seconds": 6.8
        },
        "russian": {
          "file": "references/russian/relaxed_female.flac",
          "text": "После дождя улица выглядела как новое начало. Вечерний ветер сделал город немного спокойнее.",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "language": "Russian",
              "text": "После дождя улица выглядела как новое начало. Вечерний ветер сделал город немного спокойнее.",
              "instruct": "An adult woman with a mellow, slightly husky voice and an easy, natural conversational rhythm.",
              "seed": 7906,
              "mode": "design",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign",
              "non_streaming_mode": true
            },
            "model_revision": "5ecdb67327fd37bb2e042aab12ff7391903235d3",
            "reference_sha256": null
          },
          "fingerprint": "dd5f82cd00e8c34fbb180ed219a89316cce20dc883952b91dd033f7ecb7e94e2",
          "sha256": "645553d8edce8bf61af488e5ffbad2e38cb637670663c9b9914839b259c1f8d9",
          "bytes": 193719,
          "duration_seconds": 6.24
        },
        "portuguese": {
          "file": "references/portuguese/relaxed_female.flac",
          "text": "Depois da chuva, a rua parecia um novo começo. O vento da tarde deixou a cidade um pouco mais calma.",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "language": "Portuguese",
              "text": "Depois da chuva, a rua parecia um novo começo. O vento da tarde deixou a cidade um pouco mais calma.",
              "instruct": "An adult woman with a mellow, slightly husky voice and an easy, natural conversational rhythm.",
              "seed": 8006,
              "mode": "design",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign",
              "non_streaming_mode": true
            },
            "model_revision": "5ecdb67327fd37bb2e042aab12ff7391903235d3",
            "reference_sha256": null
          },
          "fingerprint": "2492af2f0ca6e8ba6c3f836ebef0e8abd5bd2d572324011aa2fb636f15e25413",
          "sha256": "059007cdbc116324fe604f5d4b05aee78df86584e1f4ea7a510fb6ab9728bd4b",
          "bytes": 219108,
          "duration_seconds": 9.12
        },
        "spanish": {
          "file": "references/spanish/relaxed_female.flac",
          "text": "Después de la lluvia, la calle parecía un nuevo comienzo. El viento de la tarde hizo que la ciudad sonara más tranquila.",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "language": "Spanish",
              "text": "Después de la lluvia, la calle parecía un nuevo comienzo. El viento de la tarde hizo que la ciudad sonara más tranquila.",
              "instruct": "An adult woman with a mellow, slightly husky voice and an easy, natural conversational rhythm.",
              "seed": 8106,
              "mode": "design",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign",
              "non_streaming_mode": true
            },
            "model_revision": "5ecdb67327fd37bb2e042aab12ff7391903235d3",
            "reference_sha256": null
          },
          "fingerprint": "1d6ebced2a31738de6d67262e1f898a919c5b0fbd42dd460b428226f338bf759",
          "sha256": "7368a72a82dc7f06267e0bce59ed611853fa4bc6e865e2bae9886ac1a4c73f34",
          "bytes": 217277,
          "duration_seconds": 8.72
        },
        "italian": {
          "file": "references/italian/relaxed_female.flac",
          "text": "Dopo la pioggia, la strada sembrava un nuovo inizio. Il vento della sera ha reso la città più calma.",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "language": "Italian",
              "text": "Dopo la pioggia, la strada sembrava un nuovo inizio. Il vento della sera ha reso la città più calma.",
              "instruct": "An adult woman with a mellow, slightly husky voice and an easy, natural conversational rhythm.",
              "seed": 8206,
              "mode": "design",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign",
              "non_streaming_mode": true
            },
            "model_revision": "5ecdb67327fd37bb2e042aab12ff7391903235d3",
            "reference_sha256": null
          },
          "fingerprint": "95fffcb9302dacc9c59aacee293ec137099962d44d223a6ff079630d5d6cce94",
          "sha256": "4d3d2a8ce56b3c3080e209d5503c63b7e1bb20fe4072f1ecb4d7a6f2139983bd",
          "bytes": 222719,
          "duration_seconds": 7.92
        }
      },
      "reference": {
        "file": "references/relaxed_female.flac",
        "text": "The little bookshop was quiet when I arrived. Outside, the rain had stopped, and warm sunlight was finding its way through the windows.",
        "recipe": {
          "request": {
            "temperature": 0.9,
            "top_k": 50,
            "repetition_penalty": 1.05,
            "max_new_tokens": 600,
            "chunk_size": 8,
            "decoder_context_frames": 25,
            "language": "English",
            "text": "The little bookshop was quiet when I arrived. Outside, the rain had stopped, and warm sunlight was finding its way through the windows.",
            "instruct": "An adult woman with a mellow, slightly husky voice and an easy, natural conversational rhythm.",
            "seed": 7306,
            "mode": "design",
            "model": "Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign",
            "non_streaming_mode": true
          },
          "model_revision": "5ecdb67327fd37bb2e042aab12ff7391903235d3",
          "reference_sha256": null
        },
        "fingerprint": "6f2db0cb659b3efa6996949b2850d4c3fb7513548a5c8859ce259ff8e3c64b07",
        "sha256": "be45cd88d025d50a546f244603f1787668b357000709f6ec45b395cd6070b0a5",
        "bytes": 237141,
        "duration_seconds": 9.2
      }
    },
    {
      "id": "deep_male",
      "label": "Deep male",
      "design": {
        "language": "English",
        "text": "The little bookshop was quiet when I arrived. Outside, the rain had stopped, and warm sunlight was finding its way through the windows.",
        "instruct": "An older adult man with a deep gravelly bass, smooth measured pacing and the expressive warmth of a fireside storyteller.",
        "seed": 7307
      },
      "references": {
        "english": {
          "file": "references/deep_male.flac",
          "text": "The little bookshop was quiet when I arrived. Outside, the rain had stopped, and warm sunlight was finding its way through the windows.",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "language": "English",
              "text": "The little bookshop was quiet when I arrived. Outside, the rain had stopped, and warm sunlight was finding its way through the windows.",
              "instruct": "An older adult man with a deep gravelly bass, smooth measured pacing and the expressive warmth of a fireside storyteller.",
              "seed": 7307,
              "mode": "design",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign",
              "non_streaming_mode": true
            },
            "model_revision": "5ecdb67327fd37bb2e042aab12ff7391903235d3",
            "reference_sha256": null
          },
          "fingerprint": "85a1502165126ba54d6dbc70d0ba111173d5c46029904e5597835c81f8e169f0",
          "sha256": "5e2b17e08dd53f96872c11713f567c7c72f99cd0a533ec6570074ff21bd4b673",
          "bytes": 224636,
          "duration_seconds": 8.4
        },
        "chinese": {
          "file": "references/chinese/deep_male.flac",
          "text": "雨刚停，街道像重新打开的一页纸。 夜里的茶壶很安静，但好像什么都明白。",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "language": "Chinese",
              "text": "雨刚停，街道像重新打开的一页纸。 夜里的茶壶很安静，但好像什么都明白。",
              "instruct": "An older adult man with a deep gravelly bass, smooth measured pacing and the expressive warmth of a fireside storyteller.",
              "seed": 7407,
              "mode": "design",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign",
              "non_streaming_mode": true
            },
            "model_revision": "5ecdb67327fd37bb2e042aab12ff7391903235d3",
            "reference_sha256": null
          },
          "fingerprint": "79928a072a7569a9cc8e754c7819c674352ea1957fdf8085c64badc5cb68fb09",
          "sha256": "7d98baeb7fa2e63de6fa61242be6b8138a7026dc56371488b219dcb6940daa7b",
          "bytes": 284612,
          "duration_seconds": 11.44
        },
        "japanese": {
          "file": "references/japanese/deep_male.flac",
          "text": "雨上がりの道は、新しい一日のページみたいでした。 夕方の風で、街の音が少しやわらぎました。",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "language": "Japanese",
              "text": "雨上がりの道は、新しい一日のページみたいでした。 夕方の風で、街の音が少しやわらぎました。",
              "instruct": "An older adult man with a deep gravelly bass, smooth measured pacing and the expressive warmth of a fireside storyteller.",
              "seed": 7507,
              "mode": "design",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign",
              "non_streaming_mode": true
            },
            "model_revision": "5ecdb67327fd37bb2e042aab12ff7391903235d3",
            "reference_sha256": null
          },
          "fingerprint": "cda6a2c39d5b997d838dbda2a7aab0c093c5f4720e9fbad5e0d4ae27d08059a4",
          "sha256": "865291be5c1410305442e0538005a83c96c1784f64edccf161a682c4ea62eb9c",
          "bytes": 253490,
          "duration_seconds": 10.4
        },
        "korean": {
          "file": "references/korean/deep_male.flac",
          "text": "비가 그친 뒤 거리는 새로 시작하는 하루처럼 보였습니다. 저녁 바람이 도시의 소리를 조금 부드럽게 만들었습니다.",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "language": "Korean",
              "text": "비가 그친 뒤 거리는 새로 시작하는 하루처럼 보였습니다. 저녁 바람이 도시의 소리를 조금 부드럽게 만들었습니다.",
              "instruct": "An older adult man with a deep gravelly bass, smooth measured pacing and the expressive warmth of a fireside storyteller.",
              "seed": 7607,
              "mode": "design",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign",
              "non_streaming_mode": true
            },
            "model_revision": "5ecdb67327fd37bb2e042aab12ff7391903235d3",
            "reference_sha256": null
          },
          "fingerprint": "dfec44292ffdbdd368df973ba97ed1bdec5f24890694c1dd47ccd57170df1dd0",
          "sha256": "cf3b18ac6d96772977e3541b95c37f087e896dee3570d94ae058fae75d73ed3d",
          "bytes": 250357,
          "duration_seconds": 9.68
        },
        "german": {
          "file": "references/german/deep_male.flac",
          "text": "Nach dem Regen sah die Straße aus wie ein neuer Anfang. Der Abendwind machte die Stadt ein wenig freundlicher.",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "language": "German",
              "text": "Nach dem Regen sah die Straße aus wie ein neuer Anfang. Der Abendwind machte die Stadt ein wenig freundlicher.",
              "instruct": "An older adult man with a deep gravelly bass, smooth measured pacing and the expressive warmth of a fireside storyteller.",
              "seed": 7707,
              "mode": "design",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign",
              "non_streaming_mode": true
            },
            "model_revision": "5ecdb67327fd37bb2e042aab12ff7391903235d3",
            "reference_sha256": null
          },
          "fingerprint": "01fba0504499d880f6c4dbe69f5c7abc0d8e2f44a56fd4f3fb073f995db7e79d",
          "sha256": "f860f47abee5f63b78e84cf54cbbf38150d7ec3a2d970816ed0fcd34a955ea74",
          "bytes": 192332,
          "duration_seconds": 8.4
        },
        "french": {
          "file": "references/french/deep_male.flac",
          "text": "Après la pluie, la rue semblait recommencer la journée. Le vent du soir a rendu la ville un peu plus douce.",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "language": "French",
              "text": "Après la pluie, la rue semblait recommencer la journée. Le vent du soir a rendu la ville un peu plus douce.",
              "instruct": "An older adult man with a deep gravelly bass, smooth measured pacing and the expressive warmth of a fireside storyteller.",
              "seed": 7807,
              "mode": "design",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign",
              "non_streaming_mode": true
            },
            "model_revision": "5ecdb67327fd37bb2e042aab12ff7391903235d3",
            "reference_sha256": null
          },
          "fingerprint": "1b38152059bd7d8481559b8447e2539b1bbd436fd576eeb7c67e7a17a964504d",
          "sha256": "8bc971a28bb0671d1224bfd10db9e1ca1fc8477b0ea8cc45dc1d7abf3c022470",
          "bytes": 204216,
          "duration_seconds": 8.0
        },
        "russian": {
          "file": "references/russian/deep_male.flac",
          "text": "После дождя улица выглядела как новое начало. Вечерний ветер сделал город немного спокойнее.",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "language": "Russian",
              "text": "После дождя улица выглядела как новое начало. Вечерний ветер сделал город немного спокойнее.",
              "instruct": "An older adult man with a deep gravelly bass, smooth measured pacing and the expressive warmth of a fireside storyteller.",
              "seed": 7907,
              "mode": "design",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign",
              "non_streaming_mode": true
            },
            "model_revision": "5ecdb67327fd37bb2e042aab12ff7391903235d3",
            "reference_sha256": null
          },
          "fingerprint": "4458de1c36baa663c5f81b73028f730a869d7a7103009f87bb26c45c7a5b0501",
          "sha256": "7253ea073dd54cc80fca1f09dc51605c356c6c1f3ae42e64b680facd2bbd0e95",
          "bytes": 208277,
          "duration_seconds": 8.64
        },
        "portuguese": {
          "file": "references/portuguese/deep_male.flac",
          "text": "Depois da chuva, a rua parecia um novo começo. O vento da tarde deixou a cidade um pouco mais calma.",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "language": "Portuguese",
              "text": "Depois da chuva, a rua parecia um novo começo. O vento da tarde deixou a cidade um pouco mais calma.",
              "instruct": "An older adult man with a deep gravelly bass, smooth measured pacing and the expressive warmth of a fireside storyteller.",
              "seed": 8007,
              "mode": "design",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign",
              "non_streaming_mode": true
            },
            "model_revision": "5ecdb67327fd37bb2e042aab12ff7391903235d3",
            "reference_sha256": null
          },
          "fingerprint": "89cfc82c8a7c752d735539accf7443b631ae827aa374066d4cad20df20a28a0b",
          "sha256": "b1b176510519f185ad11e0135a50ee3246e1c445da9b864e1dec53cec73fb49a",
          "bytes": 260093,
          "duration_seconds": 11.52
        },
        "spanish": {
          "file": "references/spanish/deep_male.flac",
          "text": "Después de la lluvia, la calle parecía un nuevo comienzo. El viento de la tarde hizo que la ciudad sonara más tranquila.",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "language": "Spanish",
              "text": "Después de la lluvia, la calle parecía un nuevo comienzo. El viento de la tarde hizo que la ciudad sonara más tranquila.",
              "instruct": "An older adult man with a deep gravelly bass, smooth measured pacing and the expressive warmth of a fireside storyteller.",
              "seed": 8107,
              "mode": "design",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign",
              "non_streaming_mode": true
            },
            "model_revision": "5ecdb67327fd37bb2e042aab12ff7391903235d3",
            "reference_sha256": null
          },
          "fingerprint": "83aec6f4cc61a9027d24c925b988bcf72925c9d62f58910e22028bc9f4a0266c",
          "sha256": "5a574a961b460b3e9795aa465f773e99d686cfc59d900370bbfa6893a6646fee",
          "bytes": 318489,
          "duration_seconds": 10.72
        },
        "italian": {
          "file": "references/italian/deep_male.flac",
          "text": "Dopo la pioggia, la strada sembrava un nuovo inizio. Il vento della sera ha reso la città più calma.",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "language": "Italian",
              "text": "Dopo la pioggia, la strada sembrava un nuovo inizio. Il vento della sera ha reso la città più calma.",
              "instruct": "An older adult man with a deep gravelly bass, smooth measured pacing and the expressive warmth of a fireside storyteller.",
              "seed": 8207,
              "mode": "design",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign",
              "non_streaming_mode": true
            },
            "model_revision": "5ecdb67327fd37bb2e042aab12ff7391903235d3",
            "reference_sha256": null
          },
          "fingerprint": "1d313d916a8b674a4f7d6f14b31386ee686453cec3c5b78f07f809790fda11e8",
          "sha256": "fbfc0c6d4540f0e1015204a42257ca2ee9c19a36ebe5341cfb9581e15e34f99b",
          "bytes": 219068,
          "duration_seconds": 7.6
        }
      },
      "reference": {
        "file": "references/deep_male.flac",
        "text": "The little bookshop was quiet when I arrived. Outside, the rain had stopped, and warm sunlight was finding its way through the windows.",
        "recipe": {
          "request": {
            "temperature": 0.9,
            "top_k": 50,
            "repetition_penalty": 1.05,
            "max_new_tokens": 600,
            "chunk_size": 8,
            "decoder_context_frames": 25,
            "language": "English",
            "text": "The little bookshop was quiet when I arrived. Outside, the rain had stopped, and warm sunlight was finding its way through the windows.",
            "instruct": "An older adult man with a deep gravelly bass, smooth measured pacing and the expressive warmth of a fireside storyteller.",
            "seed": 7307,
            "mode": "design",
            "model": "Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign",
            "non_streaming_mode": true
          },
          "model_revision": "5ecdb67327fd37bb2e042aab12ff7391903235d3",
          "reference_sha256": null
        },
        "fingerprint": "85a1502165126ba54d6dbc70d0ba111173d5c46029904e5597835c81f8e169f0",
        "sha256": "5e2b17e08dd53f96872c11713f567c7c72f99cd0a533ec6570074ff21bd4b673",
        "bytes": 224636,
        "duration_seconds": 8.4
      }
    },
    {
      "id": "cheerful_female",
      "label": "Cheerful female",
      "design": {
        "language": "English",
        "text": "The little bookshop was quiet when I arrived. Outside, the rain had stopped, and warm sunlight was finding its way through the windows.",
        "instruct": "A cheerful adult woman with a buoyant middle-high voice, playful intonation and upbeat but natural energy.",
        "seed": 7308
      },
      "references": {
        "english": {
          "file": "references/cheerful_female.flac",
          "text": "The little bookshop was quiet when I arrived. Outside, the rain had stopped, and warm sunlight was finding its way through the windows.",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "language": "English",
              "text": "The little bookshop was quiet when I arrived. Outside, the rain had stopped, and warm sunlight was finding its way through the windows.",
              "instruct": "A cheerful adult woman with a buoyant middle-high voice, playful intonation and upbeat but natural energy.",
              "seed": 7308,
              "mode": "design",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign",
              "non_streaming_mode": true
            },
            "model_revision": "5ecdb67327fd37bb2e042aab12ff7391903235d3",
            "reference_sha256": null
          },
          "fingerprint": "7810728c439cf06d724884623e72b2bca0c3ba02f3e17157d64ac874f9ab0105",
          "sha256": "856d7c03e7d3466624ed689349faa2a590c6cd50d378ecaf93207c3a58f84953",
          "bytes": 201274,
          "duration_seconds": 7.28
        },
        "chinese": {
          "file": "references/chinese/cheerful_female.flac",
          "text": "雨刚停，街道像重新打开的一页纸。 夜里的茶壶很安静，但好像什么都明白。",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "language": "Chinese",
              "text": "雨刚停，街道像重新打开的一页纸。 夜里的茶壶很安静，但好像什么都明白。",
              "instruct": "A cheerful adult woman with a buoyant middle-high voice, playful intonation and upbeat but natural energy.",
              "seed": 7408,
              "mode": "design",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign",
              "non_streaming_mode": true
            },
            "model_revision": "5ecdb67327fd37bb2e042aab12ff7391903235d3",
            "reference_sha256": null
          },
          "fingerprint": "6b75d50ef69c1c3d2e6e2dc079a65306c63238ca1847af20d45dac01d4a4ee78",
          "sha256": "b86d64799e797a0cbd3b457ec239fe7daefd55cd7e11b697fba2b0301aeafcd6",
          "bytes": 209223,
          "duration_seconds": 7.2
        },
        "japanese": {
          "file": "references/japanese/cheerful_female.flac",
          "text": "雨上がりの道は、新しい一日のページみたいでした。 夕方の風で、街の音が少しやわらぎました。",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "language": "Japanese",
              "text": "雨上がりの道は、新しい一日のページみたいでした。 夕方の風で、街の音が少しやわらぎました。",
              "instruct": "A cheerful adult woman with a buoyant middle-high voice, playful intonation and upbeat but natural energy.",
              "seed": 7508,
              "mode": "design",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign",
              "non_streaming_mode": true
            },
            "model_revision": "5ecdb67327fd37bb2e042aab12ff7391903235d3",
            "reference_sha256": null
          },
          "fingerprint": "ee1001588e5e7e2ca8757fb7ac2d4aa7feb306774702b2e5bb3bc4d90760bff1",
          "sha256": "72a103b59d21a33cfb0b533e31905a8f5b03609e42bde1f75e582c30880ed158",
          "bytes": 245966,
          "duration_seconds": 8.32
        },
        "korean": {
          "file": "references/korean/cheerful_female.flac",
          "text": "비가 그친 뒤 거리는 새로 시작하는 하루처럼 보였습니다. 저녁 바람이 도시의 소리를 조금 부드럽게 만들었습니다.",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "language": "Korean",
              "text": "비가 그친 뒤 거리는 새로 시작하는 하루처럼 보였습니다. 저녁 바람이 도시의 소리를 조금 부드럽게 만들었습니다.",
              "instruct": "A cheerful adult woman with a buoyant middle-high voice, playful intonation and upbeat but natural energy.",
              "seed": 7608,
              "mode": "design",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign",
              "non_streaming_mode": true
            },
            "model_revision": "5ecdb67327fd37bb2e042aab12ff7391903235d3",
            "reference_sha256": null
          },
          "fingerprint": "a817610b476a5a66edf5c6325b6e5b41f81117dd189ee21f1bc0a1117b6560aa",
          "sha256": "b99687d4d2c748ad1736df3ae03f1f569d615a82c00e694a4301a8f450b0a54b",
          "bytes": 248925,
          "duration_seconds": 8.4
        },
        "german": {
          "file": "references/german/cheerful_female.flac",
          "text": "Nach dem Regen sah die Straße aus wie ein neuer Anfang. Der Abendwind machte die Stadt ein wenig freundlicher.",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "language": "German",
              "text": "Nach dem Regen sah die Straße aus wie ein neuer Anfang. Der Abendwind machte die Stadt ein wenig freundlicher.",
              "instruct": "A cheerful adult woman with a buoyant middle-high voice, playful intonation and upbeat but natural energy.",
              "seed": 7708,
              "mode": "design",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign",
              "non_streaming_mode": true
            },
            "model_revision": "5ecdb67327fd37bb2e042aab12ff7391903235d3",
            "reference_sha256": null
          },
          "fingerprint": "23e222f1a830f399d0625958dbee1001dfa24652c1bcf4386f791c21ef9442e6",
          "sha256": "21c715d0237c8970f2eb7a6b14130cfd1a51b9a373976d6e9f852d511c5adb19",
          "bytes": 189158,
          "duration_seconds": 6.48
        },
        "french": {
          "file": "references/french/cheerful_female.flac",
          "text": "Après la pluie, la rue semblait recommencer la journée. Le vent du soir a rendu la ville un peu plus douce.",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "language": "French",
              "text": "Après la pluie, la rue semblait recommencer la journée. Le vent du soir a rendu la ville un peu plus douce.",
              "instruct": "A cheerful adult woman with a buoyant middle-high voice, playful intonation and upbeat but natural energy.",
              "seed": 7808,
              "mode": "design",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign",
              "non_streaming_mode": true
            },
            "model_revision": "5ecdb67327fd37bb2e042aab12ff7391903235d3",
            "reference_sha256": null
          },
          "fingerprint": "baa324dbec501bac4ac4c2c25a7b8250dbd29351ff9e09e775a5598fe301c50f",
          "sha256": "71ae5f7ca01966ea1016ecd4466707dc500cfaca6e8b1d6b83e45e8341bce6ae",
          "bytes": 173049,
          "duration_seconds": 5.6
        },
        "russian": {
          "file": "references/russian/cheerful_female.flac",
          "text": "После дождя улица выглядела как новое начало. Вечерний ветер сделал город немного спокойнее.",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "language": "Russian",
              "text": "После дождя улица выглядела как новое начало. Вечерний ветер сделал город немного спокойнее.",
              "instruct": "A cheerful adult woman with a buoyant middle-high voice, playful intonation and upbeat but natural energy.",
              "seed": 7908,
              "mode": "design",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign",
              "non_streaming_mode": true
            },
            "model_revision": "5ecdb67327fd37bb2e042aab12ff7391903235d3",
            "reference_sha256": null
          },
          "fingerprint": "2ea765eb915ba77aff42fbde30efadf4158d0bd2b376a71ff5365425177a5c06",
          "sha256": "2bac98e29afda2f0610f67db69ba1cce9870ec79fc59953107b484604f955ef6",
          "bytes": 226745,
          "duration_seconds": 7.28
        },
        "portuguese": {
          "file": "references/portuguese/cheerful_female.flac",
          "text": "Depois da chuva, a rua parecia um novo começo. O vento da tarde deixou a cidade um pouco mais calma.",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "language": "Portuguese",
              "text": "Depois da chuva, a rua parecia um novo começo. O vento da tarde deixou a cidade um pouco mais calma.",
              "instruct": "A cheerful adult woman with a buoyant middle-high voice, playful intonation and upbeat but natural energy.",
              "seed": 8008,
              "mode": "design",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign",
              "non_streaming_mode": true
            },
            "model_revision": "5ecdb67327fd37bb2e042aab12ff7391903235d3",
            "reference_sha256": null
          },
          "fingerprint": "aeef257266273f6c847ff4cd3960c58817625bf096e28b0cf7656df1f68ecdb5",
          "sha256": "d05bc99bdf04c6424403d8007f8c86d013564f20009ef25cde4c688db7b28432",
          "bytes": 203572,
          "duration_seconds": 7.12
        },
        "spanish": {
          "file": "references/spanish/cheerful_female.flac",
          "text": "Después de la lluvia, la calle parecía un nuevo comienzo. El viento de la tarde hizo que la ciudad sonara más tranquila.",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "language": "Spanish",
              "text": "Después de la lluvia, la calle parecía un nuevo comienzo. El viento de la tarde hizo que la ciudad sonara más tranquila.",
              "instruct": "A cheerful adult woman with a buoyant middle-high voice, playful intonation and upbeat but natural energy.",
              "seed": 8108,
              "mode": "design",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign",
              "non_streaming_mode": true
            },
            "model_revision": "5ecdb67327fd37bb2e042aab12ff7391903235d3",
            "reference_sha256": null
          },
          "fingerprint": "ca6f04bfb7a151a62178c38ba2cb948270a89a4ba94b622b48be0903bbe3e2a9",
          "sha256": "cd1205ed7a2436d48634e1b128a4d3d7c4d13c5bea1018dcd86c6dad4111ac0e",
          "bytes": 240799,
          "duration_seconds": 8.16
        },
        "italian": {
          "file": "references/italian/cheerful_female.flac",
          "text": "Dopo la pioggia, la strada sembrava un nuovo inizio. Il vento della sera ha reso la città più calma.",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "language": "Italian",
              "text": "Dopo la pioggia, la strada sembrava un nuovo inizio. Il vento della sera ha reso la città più calma.",
              "instruct": "A cheerful adult woman with a buoyant middle-high voice, playful intonation and upbeat but natural energy.",
              "seed": 8208,
              "mode": "design",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign",
              "non_streaming_mode": true
            },
            "model_revision": "5ecdb67327fd37bb2e042aab12ff7391903235d3",
            "reference_sha256": null
          },
          "fingerprint": "0b829cadc00012379e509eaee6d81ab9c271956f4a52d08ac1acd9ddc5200980",
          "sha256": "c445f88bc7b3e0f4b01a0e169890d18e408b502559437c41bd351f7c6eee8013",
          "bytes": 175812,
          "duration_seconds": 6.0
        }
      },
      "reference": {
        "file": "references/cheerful_female.flac",
        "text": "The little bookshop was quiet when I arrived. Outside, the rain had stopped, and warm sunlight was finding its way through the windows.",
        "recipe": {
          "request": {
            "temperature": 0.9,
            "top_k": 50,
            "repetition_penalty": 1.05,
            "max_new_tokens": 600,
            "chunk_size": 8,
            "decoder_context_frames": 25,
            "language": "English",
            "text": "The little bookshop was quiet when I arrived. Outside, the rain had stopped, and warm sunlight was finding its way through the windows.",
            "instruct": "A cheerful adult woman with a buoyant middle-high voice, playful intonation and upbeat but natural energy.",
            "seed": 7308,
            "mode": "design",
            "model": "Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign",
            "non_streaming_mode": true
          },
          "model_revision": "5ecdb67327fd37bb2e042aab12ff7391903235d3",
          "reference_sha256": null
        },
        "fingerprint": "7810728c439cf06d724884623e72b2bca0c3ba02f3e17157d64ac874f9ab0105",
        "sha256": "856d7c03e7d3466624ed689349faa2a590c6cd50d378ecaf93207c3a58f84953",
        "bytes": 201274,
        "duration_seconds": 7.28
      }
    },
    {
      "id": "balanced_male",
      "label": "Balanced male",
      "design": {
        "language": "English",
        "text": "The little bookshop was quiet when I arrived. Outside, the rain had stopped, and warm sunlight was finding its way through the windows.",
        "instruct": "An adult man with a balanced middle register, lightly textured timbre and a relaxed, thoughtful podcast delivery.",
        "seed": 7309
      },
      "references": {
        "english": {
          "file": "references/balanced_male.flac",
          "text": "The little bookshop was quiet when I arrived. Outside, the rain had stopped, and warm sunlight was finding its way through the windows.",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "language": "English",
              "text": "The little bookshop was quiet when I arrived. Outside, the rain had stopped, and warm sunlight was finding its way through the windows.",
              "instruct": "An adult man with a balanced middle register, lightly textured timbre and a relaxed, thoughtful podcast delivery.",
              "seed": 7309,
              "mode": "design",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign",
              "non_streaming_mode": true
            },
            "model_revision": "5ecdb67327fd37bb2e042aab12ff7391903235d3",
            "reference_sha256": null
          },
          "fingerprint": "fde739dfc8498e4302cff33b6efc30176f51f9d356b9395d88496e0b567f8567",
          "sha256": "354bf6ffea71f2f7e10661df1ef833bfe609822dc16c1f02e2207ac152db3292",
          "bytes": 252877,
          "duration_seconds": 9.76
        },
        "chinese": {
          "file": "references/chinese/balanced_male.flac",
          "text": "雨刚停，街道像重新打开的一页纸。 夜里的茶壶很安静，但好像什么都明白。",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "language": "Chinese",
              "text": "雨刚停，街道像重新打开的一页纸。 夜里的茶壶很安静，但好像什么都明白。",
              "instruct": "An adult man with a balanced middle register, lightly textured timbre and a relaxed, thoughtful podcast delivery.",
              "seed": 7409,
              "mode": "design",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign",
              "non_streaming_mode": true
            },
            "model_revision": "5ecdb67327fd37bb2e042aab12ff7391903235d3",
            "reference_sha256": null
          },
          "fingerprint": "a62c9c804b478d06376b94bc92a82f957b39f6bf8323b9f03fc1f0be2223f297",
          "sha256": "41cf5df8aedcd3a1a9cdb6c0b28e4dfa0f5ab776be32aa2c9afd7dc25e877a62",
          "bytes": 209870,
          "duration_seconds": 7.92
        },
        "japanese": {
          "file": "references/japanese/balanced_male.flac",
          "text": "雨上がりの道は、新しい一日のページみたいでした。 夕方の風で、街の音が少しやわらぎました。",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "language": "Japanese",
              "text": "雨上がりの道は、新しい一日のページみたいでした。 夕方の風で、街の音が少しやわらぎました。",
              "instruct": "An adult man with a balanced middle register, lightly textured timbre and a relaxed, thoughtful podcast delivery.",
              "seed": 7509,
              "mode": "design",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign",
              "non_streaming_mode": true
            },
            "model_revision": "5ecdb67327fd37bb2e042aab12ff7391903235d3",
            "reference_sha256": null
          },
          "fingerprint": "3e4b274d7b32bfea8585bae3d5a976673a28c2c2fd7117f69691bb15beaf0896",
          "sha256": "f9a2a65656eb9278d1d0e49bc6ae17bef4cc7cb0fce7d8da8e60a5d4ea07fa3b",
          "bytes": 228428,
          "duration_seconds": 8.24
        },
        "korean": {
          "file": "references/korean/balanced_male.flac",
          "text": "비가 그친 뒤 거리는 새로 시작하는 하루처럼 보였습니다. 저녁 바람이 도시의 소리를 조금 부드럽게 만들었습니다.",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "language": "Korean",
              "text": "비가 그친 뒤 거리는 새로 시작하는 하루처럼 보였습니다. 저녁 바람이 도시의 소리를 조금 부드럽게 만들었습니다.",
              "instruct": "An adult man with a balanced middle register, lightly textured timbre and a relaxed, thoughtful podcast delivery.",
              "seed": 7609,
              "mode": "design",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign",
              "non_streaming_mode": true
            },
            "model_revision": "5ecdb67327fd37bb2e042aab12ff7391903235d3",
            "reference_sha256": null
          },
          "fingerprint": "930734d3e0f8700da371f0d791e50d62d2dbbf75d2cb5011c0c3c2f261c6c170",
          "sha256": "6e83fa9d36d3dadcf200b1b05179ea5ddfe2bb8a7c50fea89debd9312f661b70",
          "bytes": 208328,
          "duration_seconds": 8.0
        },
        "german": {
          "file": "references/german/balanced_male.flac",
          "text": "Nach dem Regen sah die Straße aus wie ein neuer Anfang. Der Abendwind machte die Stadt ein wenig freundlicher.",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "language": "German",
              "text": "Nach dem Regen sah die Straße aus wie ein neuer Anfang. Der Abendwind machte die Stadt ein wenig freundlicher.",
              "instruct": "An adult man with a balanced middle register, lightly textured timbre and a relaxed, thoughtful podcast delivery.",
              "seed": 7719,
              "mode": "design",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign",
              "non_streaming_mode": true
            },
            "model_revision": "5ecdb67327fd37bb2e042aab12ff7391903235d3",
            "reference_sha256": null
          },
          "fingerprint": "8fb6d399c3872cd158bd333993c96f5bb3ad385badc2d09d87c9ba77e666cf1d",
          "sha256": "b93c5d4fb49985721640a60596bcf4dccf21cda84d1839d2991d1fb1be2611fd",
          "bytes": 183891,
          "duration_seconds": 7.44
        },
        "french": {
          "file": "references/french/balanced_male.flac",
          "text": "Après la pluie, la rue semblait recommencer la journée. Le vent du soir a rendu la ville un peu plus douce.",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "language": "French",
              "text": "Après la pluie, la rue semblait recommencer la journée. Le vent du soir a rendu la ville un peu plus douce.",
              "instruct": "An adult man with a balanced middle register, lightly textured timbre and a relaxed, thoughtful podcast delivery.",
              "seed": 7809,
              "mode": "design",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign",
              "non_streaming_mode": true
            },
            "model_revision": "5ecdb67327fd37bb2e042aab12ff7391903235d3",
            "reference_sha256": null
          },
          "fingerprint": "1f06573abc50a3de9fd462a4b665542b08d2a0633f5bdf7ecc927b6142a98bec",
          "sha256": "6f1f57473fdf3ae7ae826e13af4a6db3ed74f919e269436a394ccb39a17c174c",
          "bytes": 189858,
          "duration_seconds": 7.28
        },
        "russian": {
          "file": "references/russian/balanced_male.flac",
          "text": "После дождя улица выглядела как новое начало. Вечерний ветер сделал город немного спокойнее.",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "language": "Russian",
              "text": "После дождя улица выглядела как новое начало. Вечерний ветер сделал город немного спокойнее.",
              "instruct": "An adult man with a balanced middle register, lightly textured timbre and a relaxed, thoughtful podcast delivery.",
              "seed": 7909,
              "mode": "design",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign",
              "non_streaming_mode": true
            },
            "model_revision": "5ecdb67327fd37bb2e042aab12ff7391903235d3",
            "reference_sha256": null
          },
          "fingerprint": "02cdec9128a3211b08e6f1d245f73aa489d124ee883d24bbb8ed97bb0b3d2581",
          "sha256": "980210ee85d2b504acb80106d8864df2a0583a691a67068516c56684c97a9163",
          "bytes": 177704,
          "duration_seconds": 6.24
        },
        "portuguese": {
          "file": "references/portuguese/balanced_male.flac",
          "text": "Depois da chuva, a rua parecia um novo começo. O vento da tarde deixou a cidade um pouco mais calma.",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "language": "Portuguese",
              "text": "Depois da chuva, a rua parecia um novo começo. O vento da tarde deixou a cidade um pouco mais calma.",
              "instruct": "An adult man with a balanced middle register, lightly textured timbre and a relaxed, thoughtful podcast delivery.",
              "seed": 8009,
              "mode": "design",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign",
              "non_streaming_mode": true
            },
            "model_revision": "5ecdb67327fd37bb2e042aab12ff7391903235d3",
            "reference_sha256": null
          },
          "fingerprint": "ff817bbc79af68d7e71508a35b9c28c4f041051e5f97be5e95558e78d252a14a",
          "sha256": "d9c06715615762b6478d3a0a48b1727ca97e8114f8465feaad412f8fd8426aee",
          "bytes": 240075,
          "duration_seconds": 9.44
        },
        "spanish": {
          "file": "references/spanish/balanced_male.flac",
          "text": "Después de la lluvia, la calle parecía un nuevo comienzo. El viento de la tarde hizo que la ciudad sonara más tranquila.",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "language": "Spanish",
              "text": "Después de la lluvia, la calle parecía un nuevo comienzo. El viento de la tarde hizo que la ciudad sonara más tranquila.",
              "instruct": "An adult man with a balanced middle register, lightly textured timbre and a relaxed, thoughtful podcast delivery.",
              "seed": 8109,
              "mode": "design",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign",
              "non_streaming_mode": true
            },
            "model_revision": "5ecdb67327fd37bb2e042aab12ff7391903235d3",
            "reference_sha256": null
          },
          "fingerprint": "bc1958751164605fadd638585738f13c070a843d24923d847290ebc88a651891",
          "sha256": "e9c7af69002888e6083ed6ec0003342bafb6fb3e4a451b7ad689fa65a0e1eb5e",
          "bytes": 221931,
          "duration_seconds": 8.32
        },
        "italian": {
          "file": "references/italian/balanced_male.flac",
          "text": "Dopo la pioggia, la strada sembrava un nuovo inizio. Il vento della sera ha reso la città più calma.",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "language": "Italian",
              "text": "Dopo la pioggia, la strada sembrava un nuovo inizio. Il vento della sera ha reso la città più calma.",
              "instruct": "An adult man with a balanced middle register, lightly textured timbre and a relaxed, thoughtful podcast delivery.",
              "seed": 8209,
              "mode": "design",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign",
              "non_streaming_mode": true
            },
            "model_revision": "5ecdb67327fd37bb2e042aab12ff7391903235d3",
            "reference_sha256": null
          },
          "fingerprint": "5fc24a11acd9e825559015aed3bbbdaa7bad90ce9e91918fecec34e382a224f2",
          "sha256": "6c862c221920e6dcc477b37c8eb9e349c51ffb2e835e3e4d482d19ba8b261617",
          "bytes": 180129,
          "duration_seconds": 6.0
        }
      },
      "reference": {
        "file": "references/balanced_male.flac",
        "text": "The little bookshop was quiet when I arrived. Outside, the rain had stopped, and warm sunlight was finding its way through the windows.",
        "recipe": {
          "request": {
            "temperature": 0.9,
            "top_k": 50,
            "repetition_penalty": 1.05,
            "max_new_tokens": 600,
            "chunk_size": 8,
            "decoder_context_frames": 25,
            "language": "English",
            "text": "The little bookshop was quiet when I arrived. Outside, the rain had stopped, and warm sunlight was finding its way through the windows.",
            "instruct": "An adult man with a balanced middle register, lightly textured timbre and a relaxed, thoughtful podcast delivery.",
            "seed": 7309,
            "mode": "design",
            "model": "Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign",
            "non_streaming_mode": true
          },
          "model_revision": "5ecdb67327fd37bb2e042aab12ff7391903235d3",
          "reference_sha256": null
        },
        "fingerprint": "fde739dfc8498e4302cff33b6efc30176f51f9d356b9395d88496e0b567f8567",
        "sha256": "354bf6ffea71f2f7e10661df1ef833bfe609822dc16c1f02e2207ac152db3292",
        "bytes": 252877,
        "duration_seconds": 9.76
      }
    }
  ],
  "reference_voice": "warm_female_narrator",
  "languages": [
    {
      "slug": "english",
      "language": "English",
      "native_name": "English",
      "icon": "EN",
      "intro_text": "Hello, this is Qwen Studio from Hangry Labs. We build local, easy-to-run voice tools so people can create speech privately, offline, and in their own language.",
      "random": [
        {
          "file": "english/random/01.opus",
          "text": "The morning coffee negotiated hard, but eventually agreed to help.",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "mode": "clone",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
              "text": "The morning coffee negotiated hard, but eventually agreed to help.",
              "language": "English",
              "seed": 8100,
              "ref_text": "The little bookshop was quiet when I arrived. Outside, the rain had stopped, and warm sunlight was finding its way through the windows.",
              "xvec_only": false,
              "non_streaming_mode": true
            },
            "model_revision": "fd4b254389122332181a7c3db7f27e918eec64e3",
            "reference_sha256": "591dc509d7be0360448d36b7a16f4e5bc8587d6096af849ffb37a69a298d7075",
            "encoding": {
              "codec": "opus",
              "container": "ogg",
              "bitrate": 64000,
              "vbr": true,
              "application": "audio",
              "compression_level": 10
            }
          },
          "fingerprint": "fa3c8f0503d2640e3a11e169e8b1f936c256095d28040cc586708657faa4f3ce",
          "sha256": "bab0752d7207f8e8dcc0e3dcf0f67866840859280055af787e1dbc4f6020cb45",
          "bytes": 35962,
          "duration_seconds": 4.087,
          "voice_profile": "warm_female_narrator",
          "reference": "references/warm_female_narrator.flac"
        },
        {
          "file": "english/random/02.opus",
          "text": "I put my keys somewhere safe, which was a bold move against myself.",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "mode": "clone",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
              "text": "I put my keys somewhere safe, which was a bold move against myself.",
              "language": "English",
              "seed": 8101,
              "ref_text": "The little bookshop was quiet when I arrived. Outside, the rain had stopped, and warm sunlight was finding its way through the windows.",
              "xvec_only": false,
              "non_streaming_mode": true
            },
            "model_revision": "fd4b254389122332181a7c3db7f27e918eec64e3",
            "reference_sha256": "dc0b1558e47ab5be575a9fa57cb85dc6612e437431d6d87d14ed05e4f15c21bb",
            "encoding": {
              "codec": "opus",
              "container": "ogg",
              "bitrate": 64000,
              "vbr": true,
              "application": "audio",
              "compression_level": 10
            }
          },
          "fingerprint": "585ceb08afc16dcd68c100be952df7fd744a92499ddfb561ef3980b39c9239e0",
          "sha256": "d36c963267752851ddf5af4e2413cc525454e96cbf2cde3571b639f8284816f4",
          "bytes": 45489,
          "duration_seconds": 4.566,
          "voice_profile": "calm_male_narrator",
          "reference": "references/calm_male_narrator.flac"
        },
        {
          "file": "english/random/03.opus",
          "text": "After the rain stopped, the street looked freshly edited.",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "mode": "clone",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
              "text": "After the rain stopped, the street looked freshly edited.",
              "language": "English",
              "seed": 8102,
              "ref_text": "The little bookshop was quiet when I arrived. Outside, the rain had stopped, and warm sunlight was finding its way through the windows.",
              "xvec_only": false,
              "non_streaming_mode": true
            },
            "model_revision": "fd4b254389122332181a7c3db7f27e918eec64e3",
            "reference_sha256": "55d956b1357debc7155a5d818d2c28bec09d75a62e83831630a4997441e56957",
            "encoding": {
              "codec": "opus",
              "container": "ogg",
              "bitrate": 64000,
              "vbr": true,
              "application": "audio",
              "compression_level": 10
            }
          },
          "fingerprint": "4c2737774cd184a2bf0b65b0ffebb1a2df79b92c989d75dd7ea318d6f9549dbe",
          "sha256": "cab4103706c22ba0694f04774091858c82131bd7627b2d772cd330911556bc8f",
          "bytes": 30201,
          "duration_seconds": 3.287,
          "voice_profile": "bright_female",
          "reference": "references/bright_female.flac"
        },
        {
          "file": "english/random/04.opus",
          "text": "The bakery smell made my detour feel like responsible planning.",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "mode": "clone",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
              "text": "The bakery smell made my detour feel like responsible planning.",
              "language": "English",
              "seed": 8103,
              "ref_text": "The little bookshop was quiet when I arrived. Outside, the rain had stopped, and warm sunlight was finding its way through the windows.",
              "xvec_only": false,
              "non_streaming_mode": true
            },
            "model_revision": "fd4b254389122332181a7c3db7f27e918eec64e3",
            "reference_sha256": "107f67576b04f5c0b050327863c198eceb9bab297daf061e4138912595183368",
            "encoding": {
              "codec": "opus",
              "container": "ogg",
              "bitrate": 64000,
              "vbr": true,
              "application": "audio",
              "compression_level": 10
            }
          },
          "fingerprint": "3ccd99c43a8d541d8cacbd4685879b762bc1919dd2aa563b0abd587e330e8284",
          "sha256": "fc8f2c8f837cc46b95ebf3e7904c68dec819b3cc41d8a83dbba6c814961b9a80",
          "bytes": 35393,
          "duration_seconds": 3.446,
          "voice_profile": "confident_male",
          "reference": "references/confident_male.flac"
        },
        {
          "file": "english/random/05.opus",
          "text": "My calendar has jokes; it put Monday right after Sunday again.",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "mode": "clone",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
              "text": "My calendar has jokes; it put Monday right after Sunday again.",
              "language": "English",
              "seed": 8104,
              "ref_text": "The little bookshop was quiet when I arrived. Outside, the rain had stopped, and warm sunlight was finding its way through the windows.",
              "xvec_only": false,
              "non_streaming_mode": true
            },
            "model_revision": "fd4b254389122332181a7c3db7f27e918eec64e3",
            "reference_sha256": "2ecedbfcc33cb3336eb218771fafaf86c5de81282162a54322658eb6df33ff54",
            "encoding": {
              "codec": "opus",
              "container": "ogg",
              "bitrate": 64000,
              "vbr": true,
              "application": "audio",
              "compression_level": 10
            }
          },
          "fingerprint": "d02bb4fcfff2ea7e9914f5a3a86c34f969f00e4896b6f79201232750092e4cb6",
          "sha256": "fc6d100bbcdfeec18836bbade6e05a4600c976a19dca5d1a0e26f554a69d8cc5",
          "bytes": 37880,
          "duration_seconds": 4.167,
          "voice_profile": "gentle_female",
          "reference": "references/gentle_female.flac"
        },
        {
          "file": "english/random/06.opus",
          "text": "I meant to send a short message and produced a tiny novel.",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "mode": "clone",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
              "text": "I meant to send a short message and produced a tiny novel.",
              "language": "English",
              "seed": 8105,
              "ref_text": "The little bookshop was quiet when I arrived. Outside, the rain had stopped, and warm sunlight was finding its way through the windows.",
              "xvec_only": false,
              "non_streaming_mode": true
            },
            "model_revision": "fd4b254389122332181a7c3db7f27e918eec64e3",
            "reference_sha256": "fdc6ccb085e5635ec60ae06463d4f7002d67461521969816f192ac4989dc36b7",
            "encoding": {
              "codec": "opus",
              "container": "ogg",
              "bitrate": 64000,
              "vbr": true,
              "application": "audio",
              "compression_level": 10
            }
          },
          "fingerprint": "0435c5c0ba2a3e39f08e9027055546fcdfec316339d67d8db7f247071bfbae8a",
          "sha256": "ea866c4e1b31641778bda3766bc8cf374f969043f11e4f984ed8cb8e5a835660",
          "bytes": 28648,
          "duration_seconds": 3.207,
          "voice_profile": "clear_male",
          "reference": "references/clear_male.flac"
        },
        {
          "file": "english/random/07.opus",
          "text": "At the market, the tomatoes looked more organized than my week.",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "mode": "clone",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
              "text": "At the market, the tomatoes looked more organized than my week.",
              "language": "English",
              "seed": 8106,
              "ref_text": "The little bookshop was quiet when I arrived. Outside, the rain had stopped, and warm sunlight was finding its way through the windows.",
              "xvec_only": false,
              "non_streaming_mode": true
            },
            "model_revision": "fd4b254389122332181a7c3db7f27e918eec64e3",
            "reference_sha256": "be45cd88d025d50a546f244603f1787668b357000709f6ec45b395cd6070b0a5",
            "encoding": {
              "codec": "opus",
              "container": "ogg",
              "bitrate": 64000,
              "vbr": true,
              "application": "audio",
              "compression_level": 10
            }
          },
          "fingerprint": "761f27428aea9becced321ad8e6a2388e6b872917905ba715d14108dd94adff9",
          "sha256": "c2d21c0d301c22243f12ae5b6d05b82405ed7c77a5ef5cf56fdb5af8fd64fbb4",
          "bytes": 34535,
          "duration_seconds": 3.926,
          "voice_profile": "relaxed_female",
          "reference": "references/relaxed_female.flac"
        },
        {
          "file": "english/random/08.opus",
          "text": "The train was late, so everyone became an expert in phone inspection.",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "mode": "clone",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
              "text": "The train was late, so everyone became an expert in phone inspection.",
              "language": "English",
              "seed": 8107,
              "ref_text": "The little bookshop was quiet when I arrived. Outside, the rain had stopped, and warm sunlight was finding its way through the windows.",
              "xvec_only": false,
              "non_streaming_mode": true
            },
            "model_revision": "fd4b254389122332181a7c3db7f27e918eec64e3",
            "reference_sha256": "5e2b17e08dd53f96872c11713f567c7c72f99cd0a533ec6570074ff21bd4b673",
            "encoding": {
              "codec": "opus",
              "container": "ogg",
              "bitrate": 64000,
              "vbr": true,
              "application": "audio",
              "compression_level": 10
            }
          },
          "fingerprint": "1eae539dd6db694a1787c972c323a9213bcce61ced56ec670e6c67c453bbb407",
          "sha256": "dd7cd5d7566c5eed6ae51b98da6eec2a4fb25619c2cc8a02b512de953ad8d538",
          "bytes": 40568,
          "duration_seconds": 4.087,
          "voice_profile": "deep_male",
          "reference": "references/deep_male.flac"
        },
        {
          "file": "english/random/09.opus",
          "text": "I cleaned my desk and found a pen from an earlier version of my life.",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "mode": "clone",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
              "text": "I cleaned my desk and found a pen from an earlier version of my life.",
              "language": "English",
              "seed": 8108,
              "ref_text": "The little bookshop was quiet when I arrived. Outside, the rain had stopped, and warm sunlight was finding its way through the windows.",
              "xvec_only": false,
              "non_streaming_mode": true
            },
            "model_revision": "fd4b254389122332181a7c3db7f27e918eec64e3",
            "reference_sha256": "856d7c03e7d3466624ed689349faa2a590c6cd50d378ecaf93207c3a58f84953",
            "encoding": {
              "codec": "opus",
              "container": "ogg",
              "bitrate": 64000,
              "vbr": true,
              "application": "audio",
              "compression_level": 10
            }
          },
          "fingerprint": "f2f6748240b4db64944b0f41f2ae268314c5642ea10ed2858fa59c13656aef36",
          "sha256": "594d139cfb0c8528c78776b6531af977aae8a3dd5554e06b0c4b8dd01bff7cf6",
          "bytes": 32234,
          "duration_seconds": 3.526,
          "voice_profile": "cheerful_female",
          "reference": "references/cheerful_female.flac"
        },
        {
          "file": "english/random/10.opus",
          "text": "The evening wind made the whole city sound a little calmer.",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "mode": "clone",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
              "text": "The evening wind made the whole city sound a little calmer.",
              "language": "English",
              "seed": 8109,
              "ref_text": "The little bookshop was quiet when I arrived. Outside, the rain had stopped, and warm sunlight was finding its way through the windows.",
              "xvec_only": false,
              "non_streaming_mode": true
            },
            "model_revision": "fd4b254389122332181a7c3db7f27e918eec64e3",
            "reference_sha256": "354bf6ffea71f2f7e10661df1ef833bfe609822dc16c1f02e2207ac152db3292",
            "encoding": {
              "codec": "opus",
              "container": "ogg",
              "bitrate": 64000,
              "vbr": true,
              "application": "audio",
              "compression_level": 10
            }
          },
          "fingerprint": "54420d0d99e8e7697d3b83cd463ef476ec0ed26a8bed1afcee44af77c6617733",
          "sha256": "8c038bf9afb9745928fabeaef865b40f4c6b6f4d0d8d7817dca0438ecdad6ebd",
          "bytes": 34233,
          "duration_seconds": 3.926,
          "voice_profile": "balanced_male",
          "reference": "references/balanced_male.flac"
        }
      ],
      "intro": [
        {
          "file": "english/intro/01.opus",
          "text": "Hello, this is Qwen Studio from Hangry Labs. We build local, easy-to-run voice tools so people can create speech privately, offline, and in their own language.",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "mode": "clone",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
              "text": "Hello, this is Qwen Studio from Hangry Labs. We build local, easy-to-run voice tools so people can create speech privately, offline, and in their own language.",
              "language": "English",
              "seed": 8500,
              "ref_text": "The little bookshop was quiet when I arrived. Outside, the rain had stopped, and warm sunlight was finding its way through the windows.",
              "xvec_only": false,
              "non_streaming_mode": true
            },
            "model_revision": "fd4b254389122332181a7c3db7f27e918eec64e3",
            "reference_sha256": "591dc509d7be0360448d36b7a16f4e5bc8587d6096af849ffb37a69a298d7075",
            "encoding": {
              "codec": "opus",
              "container": "ogg",
              "bitrate": 64000,
              "vbr": true,
              "application": "audio",
              "compression_level": 10
            }
          },
          "fingerprint": "ed91f8f950374de5726664cfa9c7bd5a3d8b361c9c2ce231f1f747b02d2b08a5",
          "sha256": "c526e67d18d9cbb086aca25f5d0d9f24345ab86b42675eda9e4d7c446e1f3e90",
          "bytes": 85757,
          "duration_seconds": 9.527,
          "voice_profile": "warm_female_narrator",
          "reference": "references/warm_female_narrator.flac"
        },
        {
          "file": "english/intro/02.opus",
          "text": "Hello, this is Qwen Studio from Hangry Labs. We build local, easy-to-run voice tools so people can create speech privately, offline, and in their own language.",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "mode": "clone",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
              "text": "Hello, this is Qwen Studio from Hangry Labs. We build local, easy-to-run voice tools so people can create speech privately, offline, and in their own language.",
              "language": "English",
              "seed": 8501,
              "ref_text": "The little bookshop was quiet when I arrived. Outside, the rain had stopped, and warm sunlight was finding its way through the windows.",
              "xvec_only": false,
              "non_streaming_mode": true
            },
            "model_revision": "fd4b254389122332181a7c3db7f27e918eec64e3",
            "reference_sha256": "107f67576b04f5c0b050327863c198eceb9bab297daf061e4138912595183368",
            "encoding": {
              "codec": "opus",
              "container": "ogg",
              "bitrate": 64000,
              "vbr": true,
              "application": "audio",
              "compression_level": 10
            }
          },
          "fingerprint": "ffd706469a0522e2d1d399a6daf0784055c945c6148e58bd05d7c96c4aae211b",
          "sha256": "3270d92f77603efb1c1c8001116533b7e99713d318d0f9d5835fb42c75a65c13",
          "bytes": 93513,
          "duration_seconds": 9.447,
          "voice_profile": "confident_male",
          "reference": "references/confident_male.flac"
        },
        {
          "file": "english/intro/03.opus",
          "text": "Hello, this is Qwen Studio from Hangry Labs. We build local, easy-to-run voice tools so people can create speech privately, offline, and in their own language.",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "mode": "clone",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
              "text": "Hello, this is Qwen Studio from Hangry Labs. We build local, easy-to-run voice tools so people can create speech privately, offline, and in their own language.",
              "language": "English",
              "seed": 8502,
              "ref_text": "The little bookshop was quiet when I arrived. Outside, the rain had stopped, and warm sunlight was finding its way through the windows.",
              "xvec_only": false,
              "non_streaming_mode": true
            },
            "model_revision": "fd4b254389122332181a7c3db7f27e918eec64e3",
            "reference_sha256": "be45cd88d025d50a546f244603f1787668b357000709f6ec45b395cd6070b0a5",
            "encoding": {
              "codec": "opus",
              "container": "ogg",
              "bitrate": 64000,
              "vbr": true,
              "application": "audio",
              "compression_level": 10
            }
          },
          "fingerprint": "e2be46563ad8be25817a030da9f095c287d561cbc1ac938193a893c7f95ac653",
          "sha256": "260eb3650eb573b22722ccd306fcd30184a6f9f94f1175b5cbdf7be0307497e4",
          "bytes": 95708,
          "duration_seconds": 10.886,
          "voice_profile": "relaxed_female",
          "reference": "references/relaxed_female.flac"
        }
      ],
      "clone": [
        {
          "file": "english/clone/01.opus",
          "text": "Hello, this is Qwen Studio from Hangry Labs. We build local, easy-to-run voice tools so people can create speech privately, offline, and in their own language.",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "mode": "clone",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
              "text": "Hello, this is Qwen Studio from Hangry Labs. We build local, easy-to-run voice tools so people can create speech privately, offline, and in their own language.",
              "language": "English",
              "seed": 8600,
              "ref_text": "The little bookshop was quiet when I arrived. Outside, the rain had stopped, and warm sunlight was finding its way through the windows.",
              "xvec_only": false,
              "non_streaming_mode": true
            },
            "model_revision": "fd4b254389122332181a7c3db7f27e918eec64e3",
            "reference_sha256": "591dc509d7be0360448d36b7a16f4e5bc8587d6096af849ffb37a69a298d7075",
            "encoding": {
              "codec": "opus",
              "container": "ogg",
              "bitrate": 64000,
              "vbr": true,
              "application": "audio",
              "compression_level": 10
            }
          },
          "fingerprint": "c1c340651ae49bc9c44ac9dbbedc17616e612c619ca6cc807cc0086416ca8b0f",
          "sha256": "94fae9e743196146b78eb20a1c8316ef8fe0602a692bffa578733f6e4248394b",
          "bytes": 93555,
          "duration_seconds": 10.646,
          "voice_profile": "warm_female_narrator",
          "reference": "references/warm_female_narrator.flac"
        }
      ]
    },
    {
      "slug": "chinese",
      "language": "Chinese",
      "native_name": "中文",
      "icon": "中",
      "intro_text": "你好，这里是 Hangry Labs 的 Qwen Studio。我们打造本地运行、容易使用的语音工具，让人们可以私密、离线地用自己的语言生成语音。",
      "random": [
        {
          "file": "chinese/random/01.opus",
          "text": "早上的咖啡像个严肃的教练，终于把我叫醒了。",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "mode": "clone",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
              "text": "早上的咖啡像个严肃的教练，终于把我叫醒了。",
              "language": "Chinese",
              "seed": 8100,
              "ref_text": "雨刚停，街道像重新打开的一页纸。 夜里的茶壶很安静，但好像什么都明白。",
              "xvec_only": false,
              "non_streaming_mode": true
            },
            "model_revision": "fd4b254389122332181a7c3db7f27e918eec64e3",
            "reference_sha256": "fca1966c27de4771410321fdc9ee9171f314d901d1606de4c64dd430b090cb75",
            "encoding": {
              "codec": "opus",
              "container": "ogg",
              "bitrate": 64000,
              "vbr": true,
              "application": "audio",
              "compression_level": 10
            }
          },
          "fingerprint": "cf766ae834bb2b749c6917e00f94aae5bcc2eecc13cbd2bece0f3b9bd5f46b54",
          "sha256": "473648ce9b92fa57ddf48d1f99717df4ab9e9b3407ee5ff5ad12fb6bade48cbc",
          "bytes": 30289,
          "duration_seconds": 3.526,
          "voice_profile": "warm_female_narrator",
          "reference": "references/chinese/warm_female_narrator.flac"
        },
        {
          "file": "chinese/random/02.opus",
          "text": "钥匙被我放在安全的地方，安全到连我自己都找不到。",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "mode": "clone",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
              "text": "钥匙被我放在安全的地方，安全到连我自己都找不到。",
              "language": "Chinese",
              "seed": 8101,
              "ref_text": "雨刚停，街道像重新打开的一页纸。 夜里的茶壶很安静，但好像什么都明白。",
              "xvec_only": false,
              "non_streaming_mode": true
            },
            "model_revision": "fd4b254389122332181a7c3db7f27e918eec64e3",
            "reference_sha256": "267600e7ddcafe29cb8cac88952cf32ef3ff8c621ab5e3fbff2ab7c0973c35e3",
            "encoding": {
              "codec": "opus",
              "container": "ogg",
              "bitrate": 64000,
              "vbr": true,
              "application": "audio",
              "compression_level": 10
            }
          },
          "fingerprint": "fe6398916eda0884437757c586c885b8e8b3fa40f89084b92eb3b79ba660e9f1",
          "sha256": "e1cbbe9e892aeb2dbb8926d470d2538c729bef2d0752622344cf92461136129a",
          "bytes": 46342,
          "duration_seconds": 4.886,
          "voice_profile": "calm_male_narrator",
          "reference": "references/chinese/calm_male_narrator.flac"
        },
        {
          "file": "chinese/random/03.opus",
          "text": "雨刚停，街道像重新打开的一页纸。",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "mode": "clone",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
              "text": "雨刚停，街道像重新打开的一页纸。",
              "language": "Chinese",
              "seed": 8102,
              "ref_text": "雨刚停，街道像重新打开的一页纸。 夜里的茶壶很安静，但好像什么都明白。",
              "xvec_only": false,
              "non_streaming_mode": true
            },
            "model_revision": "fd4b254389122332181a7c3db7f27e918eec64e3",
            "reference_sha256": "c01bdddef020b2f3eb1ea5162351ab06288395f8ff245e338f94147a64d29f99",
            "encoding": {
              "codec": "opus",
              "container": "ogg",
              "bitrate": 64000,
              "vbr": true,
              "application": "audio",
              "compression_level": 10
            }
          },
          "fingerprint": "dc97e643de42b5c0de7139d4cd2754888d895f1190e19eac8342ef4a62ec5f5f",
          "sha256": "fafd8fa31c0f018c83d6a6d0e9e0ac34621990eade7bd774c7f95c869ac96048",
          "bytes": 28381,
          "duration_seconds": 3.366,
          "voice_profile": "bright_female",
          "reference": "references/chinese/bright_female.flac"
        },
        {
          "file": "chinese/random/04.opus",
          "text": "菜市场的番茄看起来比我更有周末计划。",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "mode": "clone",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
              "text": "菜市场的番茄看起来比我更有周末计划。",
              "language": "Chinese",
              "seed": 8103,
              "ref_text": "雨刚停，街道像重新打开的一页纸。 夜里的茶壶很安静，但好像什么都明白。",
              "xvec_only": false,
              "non_streaming_mode": true
            },
            "model_revision": "fd4b254389122332181a7c3db7f27e918eec64e3",
            "reference_sha256": "a726d0fe414eaf607daf1084ba2775323fc724148fb67afe0963a39cbd2e9a07",
            "encoding": {
              "codec": "opus",
              "container": "ogg",
              "bitrate": 64000,
              "vbr": true,
              "application": "audio",
              "compression_level": 10
            }
          },
          "fingerprint": "5e25eeaca7d549fad6590f9a36780118e1150c067c85c98c324c6e4d96a070b7",
          "sha256": "86b38204e882a089cc6cbc6e6e2ea7c33475ef22e94b466f8fa5015d82478fed",
          "bytes": 27555,
          "duration_seconds": 2.567,
          "voice_profile": "confident_male",
          "reference": "references/chinese/confident_male.flac"
        },
        {
          "file": "chinese/random/05.opus",
          "text": "日历很有幽默感，又把星期一安排在星期天后面。",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "mode": "clone",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
              "text": "日历很有幽默感，又把星期一安排在星期天后面。",
              "language": "Chinese",
              "seed": 8104,
              "ref_text": "雨刚停，街道像重新打开的一页纸。 夜里的茶壶很安静，但好像什么都明白。",
              "xvec_only": false,
              "non_streaming_mode": true
            },
            "model_revision": "fd4b254389122332181a7c3db7f27e918eec64e3",
            "reference_sha256": "36480b8c4fa53b1737151dc2df6c959d83b3a3e10560b447a794b446a960647a",
            "encoding": {
              "codec": "opus",
              "container": "ogg",
              "bitrate": 64000,
              "vbr": true,
              "application": "audio",
              "compression_level": 10
            }
          },
          "fingerprint": "7df9b73a9666a6ac823ab3f45a9a8f86b0a8801fba95f78bfb6975c30c325969",
          "sha256": "7eb92c36a503305cd0bf00d26373ba12fda9bc2242e72c2bf6be0891bf3e2795",
          "bytes": 38119,
          "duration_seconds": 4.566,
          "voice_profile": "gentle_female",
          "reference": "references/chinese/gentle_female.flac"
        },
        {
          "file": "chinese/random/06.opus",
          "text": "我只想写一条短消息，结果写成了一封小论文。",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "mode": "clone",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
              "text": "我只想写一条短消息，结果写成了一封小论文。",
              "language": "Chinese",
              "seed": 8105,
              "ref_text": "雨刚停，街道像重新打开的一页纸。 夜里的茶壶很安静，但好像什么都明白。",
              "xvec_only": false,
              "non_streaming_mode": true
            },
            "model_revision": "fd4b254389122332181a7c3db7f27e918eec64e3",
            "reference_sha256": "193c397818e74f27fbe5090b6b4d087fc4d3b90db205180741b0bf9f0b373bde",
            "encoding": {
              "codec": "opus",
              "container": "ogg",
              "bitrate": 64000,
              "vbr": true,
              "application": "audio",
              "compression_level": 10
            }
          },
          "fingerprint": "410ef9c0503dee2b43a7022b9c031ae298b388739537c2bfd16adabac8d43935",
          "sha256": "54aad4e2344224078f17d7c7b27e8f62cfe74a3e51c148b182827a5371812b3c",
          "bytes": 34116,
          "duration_seconds": 3.687,
          "voice_profile": "clear_male",
          "reference": "references/chinese/clear_male.flac"
        },
        {
          "file": "chinese/random/07.opus",
          "text": "面包刚出炉，回家的路突然变得很短。",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "mode": "clone",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
              "text": "面包刚出炉，回家的路突然变得很短。",
              "language": "Chinese",
              "seed": 8106,
              "ref_text": "雨刚停，街道像重新打开的一页纸。 夜里的茶壶很安静，但好像什么都明白。",
              "xvec_only": false,
              "non_streaming_mode": true
            },
            "model_revision": "fd4b254389122332181a7c3db7f27e918eec64e3",
            "reference_sha256": "6d7c98a25d71fcb90ba2d6578f0108d7995016d326ffb1fbac56b2a0db0a0a07",
            "encoding": {
              "codec": "opus",
              "container": "ogg",
              "bitrate": 64000,
              "vbr": true,
              "application": "audio",
              "compression_level": 10
            }
          },
          "fingerprint": "5d4cb308560102f6b83d29df5012549b3c67948745c519fd4af11853d7df5699",
          "sha256": "f7fc91bd1674cc6687427a56b3b66f969301c69c3d9e6c5fee772d0943163977",
          "bytes": 33313,
          "duration_seconds": 3.926,
          "voice_profile": "relaxed_female",
          "reference": "references/chinese/relaxed_female.flac"
        },
        {
          "file": "chinese/random/08.opus",
          "text": "整理桌面时，我发现一支比计划还长寿的笔。",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "mode": "clone",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
              "text": "整理桌面时，我发现一支比计划还长寿的笔。",
              "language": "Chinese",
              "seed": 8107,
              "ref_text": "雨刚停，街道像重新打开的一页纸。 夜里的茶壶很安静，但好像什么都明白。",
              "xvec_only": false,
              "non_streaming_mode": true
            },
            "model_revision": "fd4b254389122332181a7c3db7f27e918eec64e3",
            "reference_sha256": "7d98baeb7fa2e63de6fa61242be6b8138a7026dc56371488b219dcb6940daa7b",
            "encoding": {
              "codec": "opus",
              "container": "ogg",
              "bitrate": 64000,
              "vbr": true,
              "application": "audio",
              "compression_level": 10
            }
          },
          "fingerprint": "00ed14f74c8f51113bc54b13eeb09ba9d1800d543b85004138ede735b47ebe5e",
          "sha256": "5f449e724ef926c11a78cd0633e3afad1cf6cf033db1c755626a5d273c52269e",
          "bytes": 46119,
          "duration_seconds": 4.646,
          "voice_profile": "deep_male",
          "reference": "references/chinese/deep_male.flac"
        },
        {
          "file": "chinese/random/09.opus",
          "text": "地铁稍微晚点，大家就开始认真研究手机屏幕。",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "mode": "clone",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
              "text": "地铁稍微晚点，大家就开始认真研究手机屏幕。",
              "language": "Chinese",
              "seed": 8108,
              "ref_text": "雨刚停，街道像重新打开的一页纸。 夜里的茶壶很安静，但好像什么都明白。",
              "xvec_only": false,
              "non_streaming_mode": true
            },
            "model_revision": "fd4b254389122332181a7c3db7f27e918eec64e3",
            "reference_sha256": "b86d64799e797a0cbd3b457ec239fe7daefd55cd7e11b697fba2b0301aeafcd6",
            "encoding": {
              "codec": "opus",
              "container": "ogg",
              "bitrate": 64000,
              "vbr": true,
              "application": "audio",
              "compression_level": 10
            }
          },
          "fingerprint": "54a33ac41861d148fa98217760b5cb6e8a9e2545eeb71a3268a935049ea8770f",
          "sha256": "e85edbf08d2dd2be9a282fae7e681741f2f93fb2e85bcc9083e62264092d23f5",
          "bytes": 31038,
          "duration_seconds": 3.687,
          "voice_profile": "cheerful_female",
          "reference": "references/chinese/cheerful_female.flac"
        },
        {
          "file": "chinese/random/10.opus",
          "text": "夜里的茶壶很安静，但好像什么都明白。",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "mode": "clone",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
              "text": "夜里的茶壶很安静，但好像什么都明白。",
              "language": "Chinese",
              "seed": 8109,
              "ref_text": "雨刚停，街道像重新打开的一页纸。 夜里的茶壶很安静，但好像什么都明白。",
              "xvec_only": false,
              "non_streaming_mode": true
            },
            "model_revision": "fd4b254389122332181a7c3db7f27e918eec64e3",
            "reference_sha256": "41cf5df8aedcd3a1a9cdb6c0b28e4dfa0f5ab776be32aa2c9afd7dc25e877a62",
            "encoding": {
              "codec": "opus",
              "container": "ogg",
              "bitrate": 64000,
              "vbr": true,
              "application": "audio",
              "compression_level": 10
            }
          },
          "fingerprint": "f03ea0384f3368140d264897ec52e1b21202944e070ecfc4e8dbfc233a91fcb7",
          "sha256": "e6bfb6f88ec339b8996305469413778d81baf237671a6182ed0009f7b0011a0b",
          "bytes": 31101,
          "duration_seconds": 3.767,
          "voice_profile": "balanced_male",
          "reference": "references/chinese/balanced_male.flac"
        }
      ],
      "intro": [
        {
          "file": "chinese/intro/01.opus",
          "text": "你好，这里是 Hangry Labs 的 Qwen Studio。我们打造本地运行、容易使用的语音工具，让人们可以私密、离线地用自己的语言生成语音。",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "mode": "clone",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
              "text": "你好，这里是 Hangry Labs 的 Qwen Studio。我们打造本地运行、容易使用的语音工具，让人们可以私密、离线地用自己的语言生成语音。",
              "language": "Chinese",
              "seed": 8500,
              "ref_text": "雨刚停，街道像重新打开的一页纸。 夜里的茶壶很安静，但好像什么都明白。",
              "xvec_only": false,
              "non_streaming_mode": true
            },
            "model_revision": "fd4b254389122332181a7c3db7f27e918eec64e3",
            "reference_sha256": "fca1966c27de4771410321fdc9ee9171f314d901d1606de4c64dd430b090cb75",
            "encoding": {
              "codec": "opus",
              "container": "ogg",
              "bitrate": 64000,
              "vbr": true,
              "application": "audio",
              "compression_level": 10
            }
          },
          "fingerprint": "9d674fb421a3089ade9904113c993e7fbe1b4bc482d8f50205021874b20dccf2",
          "sha256": "56a124f14b82d91cdc7419f2da2e357b6ffbd250762cdd57deb7bc4b91222ffa",
          "bytes": 93611,
          "duration_seconds": 11.046,
          "voice_profile": "warm_female_narrator",
          "reference": "references/chinese/warm_female_narrator.flac"
        },
        {
          "file": "chinese/intro/02.opus",
          "text": "你好，这里是 Hangry Labs 的 Qwen Studio。我们打造本地运行、容易使用的语音工具，让人们可以私密、离线地用自己的语言生成语音。",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "mode": "clone",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
              "text": "你好，这里是 Hangry Labs 的 Qwen Studio。我们打造本地运行、容易使用的语音工具，让人们可以私密、离线地用自己的语言生成语音。",
              "language": "Chinese",
              "seed": 8501,
              "ref_text": "雨刚停，街道像重新打开的一页纸。 夜里的茶壶很安静，但好像什么都明白。",
              "xvec_only": false,
              "non_streaming_mode": true
            },
            "model_revision": "fd4b254389122332181a7c3db7f27e918eec64e3",
            "reference_sha256": "a726d0fe414eaf607daf1084ba2775323fc724148fb67afe0963a39cbd2e9a07",
            "encoding": {
              "codec": "opus",
              "container": "ogg",
              "bitrate": 64000,
              "vbr": true,
              "application": "audio",
              "compression_level": 10
            }
          },
          "fingerprint": "f72f3c25dfea68726c56601133184a13a62cb10ef3e3014aef3f9dfeb55cc9f1",
          "sha256": "cbfac5a79053f58065f8e759b27f28de24dee1835bae6fe08353f30f4188c5c8",
          "bytes": 102454,
          "duration_seconds": 10.966,
          "voice_profile": "confident_male",
          "reference": "references/chinese/confident_male.flac"
        },
        {
          "file": "chinese/intro/03.opus",
          "text": "你好，这里是 Hangry Labs 的 Qwen Studio。我们打造本地运行、容易使用的语音工具，让人们可以私密、离线地用自己的语言生成语音。",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "mode": "clone",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
              "text": "你好，这里是 Hangry Labs 的 Qwen Studio。我们打造本地运行、容易使用的语音工具，让人们可以私密、离线地用自己的语言生成语音。",
              "language": "Chinese",
              "seed": 8502,
              "ref_text": "雨刚停，街道像重新打开的一页纸。 夜里的茶壶很安静，但好像什么都明白。",
              "xvec_only": false,
              "non_streaming_mode": true
            },
            "model_revision": "fd4b254389122332181a7c3db7f27e918eec64e3",
            "reference_sha256": "6d7c98a25d71fcb90ba2d6578f0108d7995016d326ffb1fbac56b2a0db0a0a07",
            "encoding": {
              "codec": "opus",
              "container": "ogg",
              "bitrate": 64000,
              "vbr": true,
              "application": "audio",
              "compression_level": 10
            }
          },
          "fingerprint": "be340145c387c246e3061857005a2f2046145072596211be8ba5e66d56a96f68",
          "sha256": "bc593145c09d1d451764241e3ad622d749e6a7e6b493a734bc9799a6e3092ef3",
          "bytes": 98875,
          "duration_seconds": 11.527,
          "voice_profile": "relaxed_female",
          "reference": "references/chinese/relaxed_female.flac"
        }
      ],
      "clone": [
        {
          "file": "chinese/clone/01.opus",
          "text": "你好，这里是 Hangry Labs 的 Qwen Studio。我们打造本地运行、容易使用的语音工具，让人们可以私密、离线地用自己的语言生成语音。",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "mode": "clone",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
              "text": "你好，这里是 Hangry Labs 的 Qwen Studio。我们打造本地运行、容易使用的语音工具，让人们可以私密、离线地用自己的语言生成语音。",
              "language": "Chinese",
              "seed": 8600,
              "ref_text": "The little bookshop was quiet when I arrived. Outside, the rain had stopped, and warm sunlight was finding its way through the windows.",
              "xvec_only": false,
              "non_streaming_mode": true
            },
            "model_revision": "fd4b254389122332181a7c3db7f27e918eec64e3",
            "reference_sha256": "591dc509d7be0360448d36b7a16f4e5bc8587d6096af849ffb37a69a298d7075",
            "encoding": {
              "codec": "opus",
              "container": "ogg",
              "bitrate": 64000,
              "vbr": true,
              "application": "audio",
              "compression_level": 10
            }
          },
          "fingerprint": "2bff7c1e3cef815dccd9ad2582688ad9baa040c0bb0f8bfda789d22b20b5fd50",
          "sha256": "fd83e72197d7ef67100cc0697b78efe2525abe0016d574a6dec6161735130df5",
          "bytes": 86952,
          "duration_seconds": 10.246,
          "voice_profile": "warm_female_narrator",
          "reference": "references/warm_female_narrator.flac"
        }
      ]
    },
    {
      "slug": "japanese",
      "language": "Japanese",
      "native_name": "日本語",
      "icon": "日",
      "intro_text": "こんにちは、Hangry Labs の Qwen Studio です。私たちはローカルで簡単に動かせる音声ツールを作り、誰もが自分の言語で、プライベートに、オフラインで音声を生成できるようにします。",
      "random": [
        {
          "file": "japanese/random/01.opus",
          "text": "朝のコーヒーは少し渋ったけれど、最後には助けてくれました。",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "mode": "clone",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
              "text": "朝のコーヒーは少し渋ったけれど、最後には助けてくれました。",
              "language": "Japanese",
              "seed": 8100,
              "ref_text": "雨上がりの道は、新しい一日のページみたいでした。 夕方の風で、街の音が少しやわらぎました。",
              "xvec_only": false,
              "non_streaming_mode": true
            },
            "model_revision": "fd4b254389122332181a7c3db7f27e918eec64e3",
            "reference_sha256": "858254f8ecd8a0e123fc9b224aaac7510c305126439d1229dfd10f86fd60e79c",
            "encoding": {
              "codec": "opus",
              "container": "ogg",
              "bitrate": 64000,
              "vbr": true,
              "application": "audio",
              "compression_level": 10
            }
          },
          "fingerprint": "52f970bc272af9df93943aeb5a73ec1d0e98cbeecfc0b2978476166d655f8209",
          "sha256": "407bf9562183afe9cb218a699e03190ea184a651d430c2179d9fc5eadfb1cbd8",
          "bytes": 47842,
          "duration_seconds": 5.367,
          "voice_profile": "warm_female_narrator",
          "reference": "references/japanese/warm_female_narrator.flac"
        },
        {
          "file": "japanese/random/02.opus",
          "text": "鍵を安全な場所に置いたら、安全すぎて自分でも見つかりません。",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "mode": "clone",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
              "text": "鍵を安全な場所に置いたら、安全すぎて自分でも見つかりません。",
              "language": "Japanese",
              "seed": 8101,
              "ref_text": "雨上がりの道は、新しい一日のページみたいでした。 夕方の風で、街の音が少しやわらぎました。",
              "xvec_only": false,
              "non_streaming_mode": true
            },
            "model_revision": "fd4b254389122332181a7c3db7f27e918eec64e3",
            "reference_sha256": "6f72d2c0fc2df41ec20b501823fefd7a6880509662a0c2c2e22f5c55790ad193",
            "encoding": {
              "codec": "opus",
              "container": "ogg",
              "bitrate": 64000,
              "vbr": true,
              "application": "audio",
              "compression_level": 10
            }
          },
          "fingerprint": "91eac8ae214da779b94c245d726ea0d283bb81c72fd2ce4f24811dddca353bc7",
          "sha256": "69af4b1b692497ea2677c67c34f739b17c189d15db9adb3ed35654f70ccaa4e8",
          "bytes": 42305,
          "duration_seconds": 4.167,
          "voice_profile": "calm_male_narrator",
          "reference": "references/japanese/calm_male_narrator.flac"
        },
        {
          "file": "japanese/random/03.opus",
          "text": "雨上がりの道は、新しい一日のページみたいでした。",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "mode": "clone",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
              "text": "雨上がりの道は、新しい一日のページみたいでした。",
              "language": "Japanese",
              "seed": 8102,
              "ref_text": "雨上がりの道は、新しい一日のページみたいでした。 夕方の風で、街の音が少しやわらぎました。",
              "xvec_only": false,
              "non_streaming_mode": true
            },
            "model_revision": "fd4b254389122332181a7c3db7f27e918eec64e3",
            "reference_sha256": "6b7f15fd4025c879578ec154d5943739db23d66393917c99207bf9c626dfc26e",
            "encoding": {
              "codec": "opus",
              "container": "ogg",
              "bitrate": 64000,
              "vbr": true,
              "application": "audio",
              "compression_level": 10
            }
          },
          "fingerprint": "4d33db9a4766788f2a74b6a8132e218489c49d97f087d92a7e7740a25b766f9b",
          "sha256": "b294fcbec813a4dcd6df39e03139e7e39449b6a48a4df9acab29a593c49742b4",
          "bytes": 37041,
          "duration_seconds": 4.087,
          "voice_profile": "bright_female",
          "reference": "references/japanese/bright_female.flac"
        },
        {
          "file": "japanese/random/04.opus",
          "text": "パン屋の香りで、遠回りが急に正しい判断になりました。",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "mode": "clone",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
              "text": "パン屋の香りで、遠回りが急に正しい判断になりました。",
              "language": "Japanese",
              "seed": 8103,
              "ref_text": "雨上がりの道は、新しい一日のページみたいでした。 夕方の風で、街の音が少しやわらぎました。",
              "xvec_only": false,
              "non_streaming_mode": true
            },
            "model_revision": "fd4b254389122332181a7c3db7f27e918eec64e3",
            "reference_sha256": "b2b271c5c69ddaa436592dfe7d56b464cf57dff0343b0e79559715c7e72f05b7",
            "encoding": {
              "codec": "opus",
              "container": "ogg",
              "bitrate": 64000,
              "vbr": true,
              "application": "audio",
              "compression_level": 10
            }
          },
          "fingerprint": "3e8f9762168c48be340a78bd828bc535a4473b10d3dcd8c2d85f3f22dfdde022",
          "sha256": "58e2e0cc733792add681967ee1cd4e5a380de0181a1894da58dfb9a6865ba5df",
          "bytes": 36692,
          "duration_seconds": 3.846,
          "voice_profile": "confident_male",
          "reference": "references/japanese/confident_male.flac"
        },
        {
          "file": "japanese/random/05.opus",
          "text": "カレンダーは冗談好きで、また日曜日の次に月曜日を置きました。",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "mode": "clone",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
              "text": "カレンダーは冗談好きで、また日曜日の次に月曜日を置きました。",
              "language": "Japanese",
              "seed": 8104,
              "ref_text": "雨上がりの道は、新しい一日のページみたいでした。 夕方の風で、街の音が少しやわらぎました。",
              "xvec_only": false,
              "non_streaming_mode": true
            },
            "model_revision": "fd4b254389122332181a7c3db7f27e918eec64e3",
            "reference_sha256": "fbdd730ccb29438ab1e14cb848dcda1a89d6deb84144715ce42e19da475ffc5e",
            "encoding": {
              "codec": "opus",
              "container": "ogg",
              "bitrate": 64000,
              "vbr": true,
              "application": "audio",
              "compression_level": 10
            }
          },
          "fingerprint": "aca3bb2912a83ea2afe3f0b8ef54a30a8d0d67f88b875abe387e9edba5260604",
          "sha256": "132031906a8fb49ebbe3fb46d7995e81a79a4ef83b00cef50b848567dc347d07",
          "bytes": 44425,
          "duration_seconds": 5.047,
          "voice_profile": "gentle_female",
          "reference": "references/japanese/gentle_female.flac"
        },
        {
          "file": "japanese/random/06.opus",
          "text": "短いメッセージを書くつもりが、小さな物語になりました。",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "mode": "clone",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
              "text": "短いメッセージを書くつもりが、小さな物語になりました。",
              "language": "Japanese",
              "seed": 8105,
              "ref_text": "雨上がりの道は、新しい一日のページみたいでした。 夕方の風で、街の音が少しやわらぎました。",
              "xvec_only": false,
              "non_streaming_mode": true
            },
            "model_revision": "fd4b254389122332181a7c3db7f27e918eec64e3",
            "reference_sha256": "26f2b9b45f535c430e001191d9c483a01200708e1c0e83cb20705fe50a7cdc6d",
            "encoding": {
              "codec": "opus",
              "container": "ogg",
              "bitrate": 64000,
              "vbr": true,
              "application": "audio",
              "compression_level": 10
            }
          },
          "fingerprint": "ff25e1bfa327f47cf603fab5fd3f336243d8dc1ff0f95bb45e7a2388433bf871",
          "sha256": "25148dab67d40f364042b2a4d002aeac027320aa0129898118cb0f152b4d99b1",
          "bytes": 42383,
          "duration_seconds": 4.327,
          "voice_profile": "clear_male",
          "reference": "references/japanese/clear_male.flac"
        },
        {
          "file": "japanese/random/07.opus",
          "text": "市場のトマトは、私の予定より整って見えました。",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "mode": "clone",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
              "text": "市場のトマトは、私の予定より整って見えました。",
              "language": "Japanese",
              "seed": 8106,
              "ref_text": "雨上がりの道は、新しい一日のページみたいでした。 夕方の風で、街の音が少しやわらぎました。",
              "xvec_only": false,
              "non_streaming_mode": true
            },
            "model_revision": "fd4b254389122332181a7c3db7f27e918eec64e3",
            "reference_sha256": "5e783cf091a8153c2d3c3de6551d005cfc38c3683ef2a7444143463f73667fa0",
            "encoding": {
              "codec": "opus",
              "container": "ogg",
              "bitrate": 64000,
              "vbr": true,
              "application": "audio",
              "compression_level": 10
            }
          },
          "fingerprint": "f7038aa6770b75060cc0883e7d07e4db5a4d3a06d839e585c024d2e5736ef3dd",
          "sha256": "02401bc2189f55e8415fbdf853a4f4533000c26f879b375dfdab1d8440af83e7",
          "bytes": 38291,
          "duration_seconds": 4.247,
          "voice_profile": "relaxed_female",
          "reference": "references/japanese/relaxed_female.flac"
        },
        {
          "file": "japanese/random/08.opus",
          "text": "電車が遅れて、みんな真剣にスマートフォンを眺めました。",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "mode": "clone",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
              "text": "電車が遅れて、みんな真剣にスマートフォンを眺めました。",
              "language": "Japanese",
              "seed": 8107,
              "ref_text": "雨上がりの道は、新しい一日のページみたいでした。 夕方の風で、街の音が少しやわらぎました。",
              "xvec_only": false,
              "non_streaming_mode": true
            },
            "model_revision": "fd4b254389122332181a7c3db7f27e918eec64e3",
            "reference_sha256": "865291be5c1410305442e0538005a83c96c1784f64edccf161a682c4ea62eb9c",
            "encoding": {
              "codec": "opus",
              "container": "ogg",
              "bitrate": 64000,
              "vbr": true,
              "application": "audio",
              "compression_level": 10
            }
          },
          "fingerprint": "c47d098389ff01ace0ed916e7d398ec05d819844bf4c39e62130d418f2d5415b",
          "sha256": "927659d572f9e9ffd8a2a2dce9dc0c2f269b7bfb7c7e37e6ea21892b9a59f111",
          "bytes": 41128,
          "duration_seconds": 4.327,
          "voice_profile": "deep_male",
          "reference": "references/japanese/deep_male.flac"
        },
        {
          "file": "japanese/random/09.opus",
          "text": "机を片づけたら、昔の計画から来たようなペンが出てきました。",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "mode": "clone",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
              "text": "机を片づけたら、昔の計画から来たようなペンが出てきました。",
              "language": "Japanese",
              "seed": 8108,
              "ref_text": "雨上がりの道は、新しい一日のページみたいでした。 夕方の風で、街の音が少しやわらぎました。",
              "xvec_only": false,
              "non_streaming_mode": true
            },
            "model_revision": "fd4b254389122332181a7c3db7f27e918eec64e3",
            "reference_sha256": "72a103b59d21a33cfb0b533e31905a8f5b03609e42bde1f75e582c30880ed158",
            "encoding": {
              "codec": "opus",
              "container": "ogg",
              "bitrate": 64000,
              "vbr": true,
              "application": "audio",
              "compression_level": 10
            }
          },
          "fingerprint": "3736dc5f262779b84a0be9a679a0b4087752352a905dd32d6a8689317d2dbd93",
          "sha256": "ed4f2b5a6888f56c8eb2b268eb8672b096a746a6eea60bc487c48e0f37b96fd3",
          "bytes": 46868,
          "duration_seconds": 5.127,
          "voice_profile": "cheerful_female",
          "reference": "references/japanese/cheerful_female.flac"
        },
        {
          "file": "japanese/random/10.opus",
          "text": "夕方の風で、街の音が少しやわらぎました。",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "mode": "clone",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
              "text": "夕方の風で、街の音が少しやわらぎました。",
              "language": "Japanese",
              "seed": 8109,
              "ref_text": "雨上がりの道は、新しい一日のページみたいでした。 夕方の風で、街の音が少しやわらぎました。",
              "xvec_only": false,
              "non_streaming_mode": true
            },
            "model_revision": "fd4b254389122332181a7c3db7f27e918eec64e3",
            "reference_sha256": "f9a2a65656eb9278d1d0e49bc6ae17bef4cc7cb0fce7d8da8e60a5d4ea07fa3b",
            "encoding": {
              "codec": "opus",
              "container": "ogg",
              "bitrate": 64000,
              "vbr": true,
              "application": "audio",
              "compression_level": 10
            }
          },
          "fingerprint": "8778dcf165f1683ac3a5371e65774c27ce8d5f4914b66b5be261deb6ab74392d",
          "sha256": "bd2777eb89ad0b605ae8fbc7e000e151a4c0f0b722103d56a5f02ae7e4939dce",
          "bytes": 32676,
          "duration_seconds": 3.607,
          "voice_profile": "balanced_male",
          "reference": "references/japanese/balanced_male.flac"
        }
      ],
      "intro": [
        {
          "file": "japanese/intro/01.opus",
          "text": "こんにちは、Hangry Labs の Qwen Studio です。私たちはローカルで簡単に動かせる音声ツールを作り、誰もが自分の言語で、プライベートに、オフラインで音声を生成できるようにします。",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "mode": "clone",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
              "text": "こんにちは、Hangry Labs の Qwen Studio です。私たちはローカルで簡単に動かせる音声ツールを作り、誰もが自分の言語で、プライベートに、オフラインで音声を生成できるようにします。",
              "language": "Japanese",
              "seed": 8500,
              "ref_text": "雨上がりの道は、新しい一日のページみたいでした。 夕方の風で、街の音が少しやわらぎました。",
              "xvec_only": false,
              "non_streaming_mode": true
            },
            "model_revision": "fd4b254389122332181a7c3db7f27e918eec64e3",
            "reference_sha256": "858254f8ecd8a0e123fc9b224aaac7510c305126439d1229dfd10f86fd60e79c",
            "encoding": {
              "codec": "opus",
              "container": "ogg",
              "bitrate": 64000,
              "vbr": true,
              "application": "audio",
              "compression_level": 10
            }
          },
          "fingerprint": "f988b83077409384243f8090a64b04b6549da3458e15ac24f7221eac96581f99",
          "sha256": "4714792e2c3344f3bb23c645fab442017e45cece018a004a8393f7ac29c0332c",
          "bytes": 129725,
          "duration_seconds": 14.566,
          "voice_profile": "warm_female_narrator",
          "reference": "references/japanese/warm_female_narrator.flac"
        },
        {
          "file": "japanese/intro/02.opus",
          "text": "こんにちは、Hangry Labs の Qwen Studio です。私たちはローカルで簡単に動かせる音声ツールを作り、誰もが自分の言語で、プライベートに、オフラインで音声を生成できるようにします。",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "mode": "clone",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
              "text": "こんにちは、Hangry Labs の Qwen Studio です。私たちはローカルで簡単に動かせる音声ツールを作り、誰もが自分の言語で、プライベートに、オフラインで音声を生成できるようにします。",
              "language": "Japanese",
              "seed": 8501,
              "ref_text": "雨上がりの道は、新しい一日のページみたいでした。 夕方の風で、街の音が少しやわらぎました。",
              "xvec_only": false,
              "non_streaming_mode": true
            },
            "model_revision": "fd4b254389122332181a7c3db7f27e918eec64e3",
            "reference_sha256": "b2b271c5c69ddaa436592dfe7d56b464cf57dff0343b0e79559715c7e72f05b7",
            "encoding": {
              "codec": "opus",
              "container": "ogg",
              "bitrate": 64000,
              "vbr": true,
              "application": "audio",
              "compression_level": 10
            }
          },
          "fingerprint": "6a9525730ba7f59b52324caac709a8b9c4d900eac166afc2ee22cace26c9fb06",
          "sha256": "371000b8acf37114a77b1c0e9e5b409740a3329c9e6f10fd7d751e55d2af5dd8",
          "bytes": 120531,
          "duration_seconds": 12.966,
          "voice_profile": "confident_male",
          "reference": "references/japanese/confident_male.flac"
        },
        {
          "file": "japanese/intro/03.opus",
          "text": "こんにちは、Hangry Labs の Qwen Studio です。私たちはローカルで簡単に動かせる音声ツールを作り、誰もが自分の言語で、プライベートに、オフラインで音声を生成できるようにします。",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "mode": "clone",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
              "text": "こんにちは、Hangry Labs の Qwen Studio です。私たちはローカルで簡単に動かせる音声ツールを作り、誰もが自分の言語で、プライベートに、オフラインで音声を生成できるようにします。",
              "language": "Japanese",
              "seed": 8502,
              "ref_text": "雨上がりの道は、新しい一日のページみたいでした。 夕方の風で、街の音が少しやわらぎました。",
              "xvec_only": false,
              "non_streaming_mode": true
            },
            "model_revision": "fd4b254389122332181a7c3db7f27e918eec64e3",
            "reference_sha256": "5e783cf091a8153c2d3c3de6551d005cfc38c3683ef2a7444143463f73667fa0",
            "encoding": {
              "codec": "opus",
              "container": "ogg",
              "bitrate": 64000,
              "vbr": true,
              "application": "audio",
              "compression_level": 10
            }
          },
          "fingerprint": "cc83eecc231ec4cea6e7f858128103876abb69289c329d5a47efa39616d9a757",
          "sha256": "78782aa6deb36099ff699d44809abe80e7e59c2f48e887209efa625df0cdc77b",
          "bytes": 124081,
          "duration_seconds": 14.246,
          "voice_profile": "relaxed_female",
          "reference": "references/japanese/relaxed_female.flac"
        }
      ],
      "clone": [
        {
          "file": "japanese/clone/01.opus",
          "text": "こんにちは、Hangry Labs の Qwen Studio です。私たちはローカルで簡単に動かせる音声ツールを作り、誰もが自分の言語で、プライベートに、オフラインで音声を生成できるようにします。",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "mode": "clone",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
              "text": "こんにちは、Hangry Labs の Qwen Studio です。私たちはローカルで簡単に動かせる音声ツールを作り、誰もが自分の言語で、プライベートに、オフラインで音声を生成できるようにします。",
              "language": "Japanese",
              "seed": 8600,
              "ref_text": "The little bookshop was quiet when I arrived. Outside, the rain had stopped, and warm sunlight was finding its way through the windows.",
              "xvec_only": false,
              "non_streaming_mode": true
            },
            "model_revision": "fd4b254389122332181a7c3db7f27e918eec64e3",
            "reference_sha256": "591dc509d7be0360448d36b7a16f4e5bc8587d6096af849ffb37a69a298d7075",
            "encoding": {
              "codec": "opus",
              "container": "ogg",
              "bitrate": 64000,
              "vbr": true,
              "application": "audio",
              "compression_level": 10
            }
          },
          "fingerprint": "b2f3a0902e33892ce09dc3474a63f175114391b9d1c40d87fab195d0f11d8966",
          "sha256": "2c339adb0800e47c6a04c87b2c14fbfa2d4d209a8393a4279c52496cefe3d3df",
          "bytes": 118294,
          "duration_seconds": 13.046,
          "voice_profile": "warm_female_narrator",
          "reference": "references/warm_female_narrator.flac"
        }
      ]
    },
    {
      "slug": "korean",
      "language": "Korean",
      "native_name": "한국어",
      "icon": "한",
      "intro_text": "안녕하세요, Hangry Labs의 Qwen Studio입니다. 우리는 사람들이 자신의 언어로, 개인적으로, 오프라인에서 음성을 만들 수 있도록 로컬에서 쉽게 실행되는 음성 도구를 만듭니다.",
      "random": [
        {
          "file": "korean/random/01.opus",
          "text": "아침 커피는 조금 버텼지만 결국 나를 도와주었습니다.",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "mode": "clone",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
              "text": "아침 커피는 조금 버텼지만 결국 나를 도와주었습니다.",
              "language": "Korean",
              "seed": 8100,
              "ref_text": "비가 그친 뒤 거리는 새로 시작하는 하루처럼 보였습니다. 저녁 바람이 도시의 소리를 조금 부드럽게 만들었습니다.",
              "xvec_only": false,
              "non_streaming_mode": true
            },
            "model_revision": "fd4b254389122332181a7c3db7f27e918eec64e3",
            "reference_sha256": "2aad3deb93752c5ea50d789dc56844e13bd6ac76cca9484057f47f3b54f41d74",
            "encoding": {
              "codec": "opus",
              "container": "ogg",
              "bitrate": 64000,
              "vbr": true,
              "application": "audio",
              "compression_level": 10
            }
          },
          "fingerprint": "cda2b070ace46eaf4322a684381d41d80effe96ab9fdf2b85c932e1cd6f80150",
          "sha256": "0d2dacb6b9aee541a7858d34ba07f025c2cb26bdf14abe30bcd9249ea0718e4f",
          "bytes": 35912,
          "duration_seconds": 4.487,
          "voice_profile": "warm_female_narrator",
          "reference": "references/korean/warm_female_narrator.flac"
        },
        {
          "file": "korean/random/02.opus",
          "text": "열쇠를 안전한 곳에 두었더니 너무 안전해서 못 찾겠습니다.",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "mode": "clone",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
              "text": "열쇠를 안전한 곳에 두었더니 너무 안전해서 못 찾겠습니다.",
              "language": "Korean",
              "seed": 8101,
              "ref_text": "비가 그친 뒤 거리는 새로 시작하는 하루처럼 보였습니다. 저녁 바람이 도시의 소리를 조금 부드럽게 만들었습니다.",
              "xvec_only": false,
              "non_streaming_mode": true
            },
            "model_revision": "fd4b254389122332181a7c3db7f27e918eec64e3",
            "reference_sha256": "cb1af396f7c17621f7c4290507f7292aa0f3fafe67728ad6340486d0dfaf535e",
            "encoding": {
              "codec": "opus",
              "container": "ogg",
              "bitrate": 64000,
              "vbr": true,
              "application": "audio",
              "compression_level": 10
            }
          },
          "fingerprint": "1c72410a75db2a4e9ba4e605ce93ab548c22c66e90d74f9ef828a57f2aca91c3",
          "sha256": "055b5cc517f2fb19ab0a5a7ca9063ff815ae23e6fe3d0169ff0c8c4e4d544adb",
          "bytes": 38581,
          "duration_seconds": 4.247,
          "voice_profile": "calm_male_narrator",
          "reference": "references/korean/calm_male_narrator.flac"
        },
        {
          "file": "korean/random/03.opus",
          "text": "비가 그친 뒤 거리는 새로 시작하는 하루처럼 보였습니다.",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "mode": "clone",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
              "text": "비가 그친 뒤 거리는 새로 시작하는 하루처럼 보였습니다.",
              "language": "Korean",
              "seed": 8102,
              "ref_text": "비가 그친 뒤 거리는 새로 시작하는 하루처럼 보였습니다. 저녁 바람이 도시의 소리를 조금 부드럽게 만들었습니다.",
              "xvec_only": false,
              "non_streaming_mode": true
            },
            "model_revision": "fd4b254389122332181a7c3db7f27e918eec64e3",
            "reference_sha256": "6080f008269cd96699b32f26387248166fdaa71f364568bd4f0a46e5f5e80750",
            "encoding": {
              "codec": "opus",
              "container": "ogg",
              "bitrate": 64000,
              "vbr": true,
              "application": "audio",
              "compression_level": 10
            }
          },
          "fingerprint": "07005ab461b0f269c5c6d5c2f496bea18c8508146b9914d6924e7125348cf575",
          "sha256": "8b3fc8939f83370bc92c3eb79b16970bcb1eee2cd7a253e5dc1ee3a1b139a074",
          "bytes": 41637,
          "duration_seconds": 5.207,
          "voice_profile": "bright_female",
          "reference": "references/korean/bright_female.flac"
        },
        {
          "file": "korean/random/04.opus",
          "text": "빵집 냄새 덕분에 돌아가는 길도 합리적인 선택이 되었습니다.",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "mode": "clone",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
              "text": "빵집 냄새 덕분에 돌아가는 길도 합리적인 선택이 되었습니다.",
              "language": "Korean",
              "seed": 8103,
              "ref_text": "비가 그친 뒤 거리는 새로 시작하는 하루처럼 보였습니다. 저녁 바람이 도시의 소리를 조금 부드럽게 만들었습니다.",
              "xvec_only": false,
              "non_streaming_mode": true
            },
            "model_revision": "fd4b254389122332181a7c3db7f27e918eec64e3",
            "reference_sha256": "abb5934d20218e2670421316207e4cb9e35c80c0d039c55043c6bbb77c26090c",
            "encoding": {
              "codec": "opus",
              "container": "ogg",
              "bitrate": 64000,
              "vbr": true,
              "application": "audio",
              "compression_level": 10
            }
          },
          "fingerprint": "57dd31c7ac6727ca040ad5f17e8137d375c2269ea20df380402063c8834a67c3",
          "sha256": "9caea185493bcf95a94a1522f2ad8869c288738bc473641e49a56ac2dccd1fca",
          "bytes": 38317,
          "duration_seconds": 4.487,
          "voice_profile": "confident_male",
          "reference": "references/korean/confident_male.flac"
        },
        {
          "file": "korean/random/05.opus",
          "text": "달력은 농담을 좋아해서 또 일요일 다음에 월요일을 놓았습니다.",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "mode": "clone",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
              "text": "달력은 농담을 좋아해서 또 일요일 다음에 월요일을 놓았습니다.",
              "language": "Korean",
              "seed": 8104,
              "ref_text": "비가 그친 뒤 거리는 새로 시작하는 하루처럼 보였습니다. 저녁 바람이 도시의 소리를 조금 부드럽게 만들었습니다.",
              "xvec_only": false,
              "non_streaming_mode": true
            },
            "model_revision": "fd4b254389122332181a7c3db7f27e918eec64e3",
            "reference_sha256": "deb07ad7edecf6b88f03ac6ce20bf0892d2596cdd6c53f10a39a74c1b4ed3d00",
            "encoding": {
              "codec": "opus",
              "container": "ogg",
              "bitrate": 64000,
              "vbr": true,
              "application": "audio",
              "compression_level": 10
            }
          },
          "fingerprint": "4620ac9e229e21ea89808ad7cd59487f90ff5a78a0e655a2e04bc6c8981acc13",
          "sha256": "19f0a95a97623d034ae8100220ed76fa939095aad15277e42abd866157b5b62e",
          "bytes": 41767,
          "duration_seconds": 5.287,
          "voice_profile": "gentle_female",
          "reference": "references/korean/gentle_female.flac"
        },
        {
          "file": "korean/random/06.opus",
          "text": "짧은 메시지를 쓰려다 작은 이야기가 되었습니다.",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "mode": "clone",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
              "text": "짧은 메시지를 쓰려다 작은 이야기가 되었습니다.",
              "language": "Korean",
              "seed": 8105,
              "ref_text": "비가 그친 뒤 거리는 새로 시작하는 하루처럼 보였습니다. 저녁 바람이 도시의 소리를 조금 부드럽게 만들었습니다.",
              "xvec_only": false,
              "non_streaming_mode": true
            },
            "model_revision": "fd4b254389122332181a7c3db7f27e918eec64e3",
            "reference_sha256": "299820179a682766cf1a767e8c5cffdcc02f7df853b409a70095a0c2889da51b",
            "encoding": {
              "codec": "opus",
              "container": "ogg",
              "bitrate": 64000,
              "vbr": true,
              "application": "audio",
              "compression_level": 10
            }
          },
          "fingerprint": "c785dd12018e5fb51a17c0c90cda92856f36966cd1ae2fa0e2fceed854bd7028",
          "sha256": "3c294d487ca1e4167a42f2a54e4f0693acd71824196a113c104716bd7621114d",
          "bytes": 36478,
          "duration_seconds": 4.487,
          "voice_profile": "clear_male",
          "reference": "references/korean/clear_male.flac"
        },
        {
          "file": "korean/random/07.opus",
          "text": "시장의 토마토가 내 한 주보다 더 잘 정리되어 보였습니다.",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "mode": "clone",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
              "text": "시장의 토마토가 내 한 주보다 더 잘 정리되어 보였습니다.",
              "language": "Korean",
              "seed": 8106,
              "ref_text": "비가 그친 뒤 거리는 새로 시작하는 하루처럼 보였습니다. 저녁 바람이 도시의 소리를 조금 부드럽게 만들었습니다.",
              "xvec_only": false,
              "non_streaming_mode": true
            },
            "model_revision": "fd4b254389122332181a7c3db7f27e918eec64e3",
            "reference_sha256": "7ce1df486a113bf47365d73cc1ce166d5f696fedb9843ac56614b82b281a1c9f",
            "encoding": {
              "codec": "opus",
              "container": "ogg",
              "bitrate": 64000,
              "vbr": true,
              "application": "audio",
              "compression_level": 10
            }
          },
          "fingerprint": "1597d2d37bdf334e77b8ea01de19e9ab617da41d65990836cf8820d6ef911356",
          "sha256": "1603983ebf89496325fbdef3e3ae1d607e144b959f1566426e599a1fd8817bd9",
          "bytes": 38628,
          "duration_seconds": 4.726,
          "voice_profile": "relaxed_female",
          "reference": "references/korean/relaxed_female.flac"
        },
        {
          "file": "korean/random/08.opus",
          "text": "기차가 늦어서 모두 진지하게 휴대폰을 바라보았습니다.",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "mode": "clone",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
              "text": "기차가 늦어서 모두 진지하게 휴대폰을 바라보았습니다.",
              "language": "Korean",
              "seed": 8107,
              "ref_text": "비가 그친 뒤 거리는 새로 시작하는 하루처럼 보였습니다. 저녁 바람이 도시의 소리를 조금 부드럽게 만들었습니다.",
              "xvec_only": false,
              "non_streaming_mode": true
            },
            "model_revision": "fd4b254389122332181a7c3db7f27e918eec64e3",
            "reference_sha256": "cf3b18ac6d96772977e3541b95c37f087e896dee3570d94ae058fae75d73ed3d",
            "encoding": {
              "codec": "opus",
              "container": "ogg",
              "bitrate": 64000,
              "vbr": true,
              "application": "audio",
              "compression_level": 10
            }
          },
          "fingerprint": "d9b6df7575f542807de79151b1bf05f3a289a099b6047bdc9d0505420e09d2e6",
          "sha256": "4aec5e48eb2715ebfad73d8be7f00ff494509abd2875dd1807e2da864d520f29",
          "bytes": 36936,
          "duration_seconds": 4.247,
          "voice_profile": "deep_male",
          "reference": "references/korean/deep_male.flac"
        },
        {
          "file": "korean/random/09.opus",
          "text": "책상을 정리하다가 오래된 계획 속 펜을 찾았습니다.",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "mode": "clone",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
              "text": "책상을 정리하다가 오래된 계획 속 펜을 찾았습니다.",
              "language": "Korean",
              "seed": 8108,
              "ref_text": "비가 그친 뒤 거리는 새로 시작하는 하루처럼 보였습니다. 저녁 바람이 도시의 소리를 조금 부드럽게 만들었습니다.",
              "xvec_only": false,
              "non_streaming_mode": true
            },
            "model_revision": "fd4b254389122332181a7c3db7f27e918eec64e3",
            "reference_sha256": "b99687d4d2c748ad1736df3ae03f1f569d615a82c00e694a4301a8f450b0a54b",
            "encoding": {
              "codec": "opus",
              "container": "ogg",
              "bitrate": 64000,
              "vbr": true,
              "application": "audio",
              "compression_level": 10
            }
          },
          "fingerprint": "e6b1ba5fa1c53f28eaf6506098bc0ee8e3391724edb46a6dea27b2493606d158",
          "sha256": "0641f5553e9d1109f698f4f5c6b1d365d3d1d8e730bbb140577c736c23955ad8",
          "bytes": 35539,
          "duration_seconds": 4.327,
          "voice_profile": "cheerful_female",
          "reference": "references/korean/cheerful_female.flac"
        },
        {
          "file": "korean/random/10.opus",
          "text": "저녁 바람이 도시의 소리를 조금 부드럽게 만들었습니다.",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "mode": "clone",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
              "text": "저녁 바람이 도시의 소리를 조금 부드럽게 만들었습니다.",
              "language": "Korean",
              "seed": 8109,
              "ref_text": "비가 그친 뒤 거리는 새로 시작하는 하루처럼 보였습니다. 저녁 바람이 도시의 소리를 조금 부드럽게 만들었습니다.",
              "xvec_only": false,
              "non_streaming_mode": true
            },
            "model_revision": "fd4b254389122332181a7c3db7f27e918eec64e3",
            "reference_sha256": "6e83fa9d36d3dadcf200b1b05179ea5ddfe2bb8a7c50fea89debd9312f661b70",
            "encoding": {
              "codec": "opus",
              "container": "ogg",
              "bitrate": 64000,
              "vbr": true,
              "application": "audio",
              "compression_level": 10
            }
          },
          "fingerprint": "32804d417d4dc512447440d997ae1c354d1f9972150bb0c3700d5dd677c5afb8",
          "sha256": "ab34dccc1ded6a6573dff51ecff333bc555a22f51f06cd7b39fa4c186f17cf85",
          "bytes": 34202,
          "duration_seconds": 4.087,
          "voice_profile": "balanced_male",
          "reference": "references/korean/balanced_male.flac"
        }
      ],
      "intro": [
        {
          "file": "korean/intro/01.opus",
          "text": "안녕하세요, Hangry Labs의 Qwen Studio입니다. 우리는 사람들이 자신의 언어로, 개인적으로, 오프라인에서 음성을 만들 수 있도록 로컬에서 쉽게 실행되는 음성 도구를 만듭니다.",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "mode": "clone",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
              "text": "안녕하세요, Hangry Labs의 Qwen Studio입니다. 우리는 사람들이 자신의 언어로, 개인적으로, 오프라인에서 음성을 만들 수 있도록 로컬에서 쉽게 실행되는 음성 도구를 만듭니다.",
              "language": "Korean",
              "seed": 8500,
              "ref_text": "비가 그친 뒤 거리는 새로 시작하는 하루처럼 보였습니다. 저녁 바람이 도시의 소리를 조금 부드럽게 만들었습니다.",
              "xvec_only": false,
              "non_streaming_mode": true
            },
            "model_revision": "fd4b254389122332181a7c3db7f27e918eec64e3",
            "reference_sha256": "2aad3deb93752c5ea50d789dc56844e13bd6ac76cca9484057f47f3b54f41d74",
            "encoding": {
              "codec": "opus",
              "container": "ogg",
              "bitrate": 64000,
              "vbr": true,
              "application": "audio",
              "compression_level": 10
            }
          },
          "fingerprint": "2406ef64944fdf3ad234f482fc52e70452afbe638cbe757b616ab21ed82e3c43",
          "sha256": "08eae897470ad08718d4f54f1f84912051789cac4fd2b184bc480760b315aa4f",
          "bytes": 108176,
          "duration_seconds": 13.367,
          "voice_profile": "warm_female_narrator",
          "reference": "references/korean/warm_female_narrator.flac"
        },
        {
          "file": "korean/intro/02.opus",
          "text": "안녕하세요, Hangry Labs의 Qwen Studio입니다. 우리는 사람들이 자신의 언어로, 개인적으로, 오프라인에서 음성을 만들 수 있도록 로컬에서 쉽게 실행되는 음성 도구를 만듭니다.",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "mode": "clone",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
              "text": "안녕하세요, Hangry Labs의 Qwen Studio입니다. 우리는 사람들이 자신의 언어로, 개인적으로, 오프라인에서 음성을 만들 수 있도록 로컬에서 쉽게 실행되는 음성 도구를 만듭니다.",
              "language": "Korean",
              "seed": 8501,
              "ref_text": "비가 그친 뒤 거리는 새로 시작하는 하루처럼 보였습니다. 저녁 바람이 도시의 소리를 조금 부드럽게 만들었습니다.",
              "xvec_only": false,
              "non_streaming_mode": true
            },
            "model_revision": "fd4b254389122332181a7c3db7f27e918eec64e3",
            "reference_sha256": "abb5934d20218e2670421316207e4cb9e35c80c0d039c55043c6bbb77c26090c",
            "encoding": {
              "codec": "opus",
              "container": "ogg",
              "bitrate": 64000,
              "vbr": true,
              "application": "audio",
              "compression_level": 10
            }
          },
          "fingerprint": "c24f8766004e434608fc56ce963777a63934563e73da98c8915cf04e25288e53",
          "sha256": "571700a61e011bd5e4f0a871a887a6994097ec289780b018cafb62c2d299f45c",
          "bytes": 125369,
          "duration_seconds": 14.007,
          "voice_profile": "confident_male",
          "reference": "references/korean/confident_male.flac"
        },
        {
          "file": "korean/intro/03.opus",
          "text": "안녕하세요, Hangry Labs의 Qwen Studio입니다. 우리는 사람들이 자신의 언어로, 개인적으로, 오프라인에서 음성을 만들 수 있도록 로컬에서 쉽게 실행되는 음성 도구를 만듭니다.",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "mode": "clone",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
              "text": "안녕하세요, Hangry Labs의 Qwen Studio입니다. 우리는 사람들이 자신의 언어로, 개인적으로, 오프라인에서 음성을 만들 수 있도록 로컬에서 쉽게 실행되는 음성 도구를 만듭니다.",
              "language": "Korean",
              "seed": 8502,
              "ref_text": "비가 그친 뒤 거리는 새로 시작하는 하루처럼 보였습니다. 저녁 바람이 도시의 소리를 조금 부드럽게 만들었습니다.",
              "xvec_only": false,
              "non_streaming_mode": true
            },
            "model_revision": "fd4b254389122332181a7c3db7f27e918eec64e3",
            "reference_sha256": "7ce1df486a113bf47365d73cc1ce166d5f696fedb9843ac56614b82b281a1c9f",
            "encoding": {
              "codec": "opus",
              "container": "ogg",
              "bitrate": 64000,
              "vbr": true,
              "application": "audio",
              "compression_level": 10
            }
          },
          "fingerprint": "6bb69d171af5ee0ef9578aafd6f15f9d3eaf753afd3b5055eeb40a329cf30af3",
          "sha256": "b76adec5905697642f7b647cf7a36d7af9e6ca5a0937eabc8829097c80a714c6",
          "bytes": 118322,
          "duration_seconds": 14.166,
          "voice_profile": "relaxed_female",
          "reference": "references/korean/relaxed_female.flac"
        }
      ],
      "clone": [
        {
          "file": "korean/clone/01.opus",
          "text": "안녕하세요, Hangry Labs의 Qwen Studio입니다. 우리는 사람들이 자신의 언어로, 개인적으로, 오프라인에서 음성을 만들 수 있도록 로컬에서 쉽게 실행되는 음성 도구를 만듭니다.",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "mode": "clone",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
              "text": "안녕하세요, Hangry Labs의 Qwen Studio입니다. 우리는 사람들이 자신의 언어로, 개인적으로, 오프라인에서 음성을 만들 수 있도록 로컬에서 쉽게 실행되는 음성 도구를 만듭니다.",
              "language": "Korean",
              "seed": 8600,
              "ref_text": "The little bookshop was quiet when I arrived. Outside, the rain had stopped, and warm sunlight was finding its way through the windows.",
              "xvec_only": false,
              "non_streaming_mode": true
            },
            "model_revision": "fd4b254389122332181a7c3db7f27e918eec64e3",
            "reference_sha256": "591dc509d7be0360448d36b7a16f4e5bc8587d6096af849ffb37a69a298d7075",
            "encoding": {
              "codec": "opus",
              "container": "ogg",
              "bitrate": 64000,
              "vbr": true,
              "application": "audio",
              "compression_level": 10
            }
          },
          "fingerprint": "a3bd2e5d88bb4fe21851041b2745471a08fd3f417979805d8b65f24bf913ce5b",
          "sha256": "d6ab4cb5e68ce05028fee629c2d218a37369791d91efc26103a2d6ec4adfa2bb",
          "bytes": 110023,
          "duration_seconds": 13.367,
          "voice_profile": "warm_female_narrator",
          "reference": "references/warm_female_narrator.flac"
        }
      ]
    },
    {
      "slug": "german",
      "language": "German",
      "native_name": "Deutsch",
      "icon": "DE",
      "intro_text": "Hallo, hier ist Qwen Studio von Hangry Labs. Wir bauen lokale, einfach startbare Sprachwerkzeuge, damit Menschen privat, offline und in ihrer eigenen Sprache Sprache erzeugen können.",
      "random": [
        {
          "file": "german/random/01.opus",
          "text": "Der Morgenkaffee verhandelte hart, half dann aber doch.",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "mode": "clone",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
              "text": "Der Morgenkaffee verhandelte hart, half dann aber doch.",
              "language": "German",
              "seed": 8100,
              "ref_text": "Nach dem Regen sah die Straße aus wie ein neuer Anfang. Der Abendwind machte die Stadt ein wenig freundlicher.",
              "xvec_only": false,
              "non_streaming_mode": true
            },
            "model_revision": "fd4b254389122332181a7c3db7f27e918eec64e3",
            "reference_sha256": "62f2514f9aaa43b9695c8dc9190d3fbd431ca13ddcb4573e4f7065cb37b3224d",
            "encoding": {
              "codec": "opus",
              "container": "ogg",
              "bitrate": 64000,
              "vbr": true,
              "application": "audio",
              "compression_level": 10
            }
          },
          "fingerprint": "978136212f869eae6ba1f092abe8d22a1dd24b68984de150797c6089f8d12f3a",
          "sha256": "a3cad40f6f0936e06dd99874008695c473b809d41cc27e1082c7e4cc5c4dcb41",
          "bytes": 33913,
          "duration_seconds": 3.846,
          "voice_profile": "warm_female_narrator",
          "reference": "references/german/warm_female_narrator.flac"
        },
        {
          "file": "german/random/02.opus",
          "text": "Ich legte die Schlüssel an einen sicheren Ort, leider zu sicher.",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "mode": "clone",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
              "text": "Ich legte die Schlüssel an einen sicheren Ort, leider zu sicher.",
              "language": "German",
              "seed": 8101,
              "ref_text": "Nach dem Regen sah die Straße aus wie ein neuer Anfang. Der Abendwind machte die Stadt ein wenig freundlicher.",
              "xvec_only": false,
              "non_streaming_mode": true
            },
            "model_revision": "fd4b254389122332181a7c3db7f27e918eec64e3",
            "reference_sha256": "9e1b9440d2894db533c18fdf2e4200d4396aeb28f9a1dadf41e65a3bb12944c1",
            "encoding": {
              "codec": "opus",
              "container": "ogg",
              "bitrate": 64000,
              "vbr": true,
              "application": "audio",
              "compression_level": 10
            }
          },
          "fingerprint": "c726d6fc6783ad721291df3ff0b9a5df0c726e2f106b282818b64e9202559c3b",
          "sha256": "d3ad766884000713e2769f449c3afd6ca7be7133e4fd9fb70501e7ec6926d677",
          "bytes": 36373,
          "duration_seconds": 3.687,
          "voice_profile": "calm_male_narrator",
          "reference": "references/german/calm_male_narrator.flac"
        },
        {
          "file": "german/random/03.opus",
          "text": "Nach dem Regen sah die Straße aus wie ein neuer Anfang.",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "mode": "clone",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
              "text": "Nach dem Regen sah die Straße aus wie ein neuer Anfang.",
              "language": "German",
              "seed": 8102,
              "ref_text": "Nach dem Regen sah die Straße aus wie ein neuer Anfang. Der Abendwind machte die Stadt ein wenig freundlicher.",
              "xvec_only": false,
              "non_streaming_mode": true
            },
            "model_revision": "fd4b254389122332181a7c3db7f27e918eec64e3",
            "reference_sha256": "d5171ddcf4420c8c7703b32a02959f51d900a967d69b628ae202c085e89a1a03",
            "encoding": {
              "codec": "opus",
              "container": "ogg",
              "bitrate": 64000,
              "vbr": true,
              "application": "audio",
              "compression_level": 10
            }
          },
          "fingerprint": "a00d4da3d9c87692b5fa6cb47d7c2ed9bfd9a9f01d1337dd06a9d2b68ae6b7f8",
          "sha256": "f1fca0f959bfb751ff95ee2e46e9ef16abc4dacaf2061ce6914cfa45fefc2d82",
          "bytes": 28763,
          "duration_seconds": 3.046,
          "voice_profile": "bright_female",
          "reference": "references/german/bright_female.flac"
        },
        {
          "file": "german/random/04.opus",
          "text": "Der Duft der Bäckerei machte den Umweg völlig vernünftig.",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "mode": "clone",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
              "text": "Der Duft der Bäckerei machte den Umweg völlig vernünftig.",
              "language": "German",
              "seed": 8103,
              "ref_text": "Nach dem Regen sah die Straße aus wie ein neuer Anfang. Der Abendwind machte die Stadt ein wenig freundlicher.",
              "xvec_only": false,
              "non_streaming_mode": true
            },
            "model_revision": "fd4b254389122332181a7c3db7f27e918eec64e3",
            "reference_sha256": "d57bcf128cf022cdea552927c876c1f283aa3559cf496bf733375c619be7b9b3",
            "encoding": {
              "codec": "opus",
              "container": "ogg",
              "bitrate": 64000,
              "vbr": true,
              "application": "audio",
              "compression_level": 10
            }
          },
          "fingerprint": "bfd8a67692aadb2b89157f68d2c1b7c525a0ff989d215618ffc10a0b93c1d58e",
          "sha256": "f070e119ed706021fd8b9ca38df5076ed9cbd82cfa55cd70f6fd8d825543d42a",
          "bytes": 29310,
          "duration_seconds": 2.886,
          "voice_profile": "confident_male",
          "reference": "references/german/confident_male.flac"
        },
        {
          "file": "german/random/05.opus",
          "text": "Mein Kalender hat Humor; Montag kommt wieder direkt nach Sonntag.",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "mode": "clone",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
              "text": "Mein Kalender hat Humor; Montag kommt wieder direkt nach Sonntag.",
              "language": "German",
              "seed": 8104,
              "ref_text": "Nach dem Regen sah die Straße aus wie ein neuer Anfang. Der Abendwind machte die Stadt ein wenig freundlicher.",
              "xvec_only": false,
              "non_streaming_mode": true
            },
            "model_revision": "fd4b254389122332181a7c3db7f27e918eec64e3",
            "reference_sha256": "fe76a572a92edf07b88e19be7080fb95a18eccf79ad191745936b970048e07b6",
            "encoding": {
              "codec": "opus",
              "container": "ogg",
              "bitrate": 64000,
              "vbr": true,
              "application": "audio",
              "compression_level": 10
            }
          },
          "fingerprint": "d737992ea21e92ab265851dc6a81d0830b8beffe9116cf8b106e19c565ae24e2",
          "sha256": "b6ae7fe26d3036de0100bcf45b78dd6c022dc302381d309bb2dffd2646883501",
          "bytes": 39612,
          "duration_seconds": 4.566,
          "voice_profile": "gentle_female",
          "reference": "references/german/gentle_female.flac"
        },
        {
          "file": "german/random/06.opus",
          "text": "Ich wollte eine kurze Nachricht schreiben und landete bei einem kleinen Roman.",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "mode": "clone",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
              "text": "Ich wollte eine kurze Nachricht schreiben und landete bei einem kleinen Roman.",
              "language": "German",
              "seed": 8105,
              "ref_text": "Nach dem Regen sah die Straße aus wie ein neuer Anfang. Der Abendwind machte die Stadt ein wenig freundlicher.",
              "xvec_only": false,
              "non_streaming_mode": true
            },
            "model_revision": "fd4b254389122332181a7c3db7f27e918eec64e3",
            "reference_sha256": "beb7c0d5bddf0cb5576a1578a5724e1fce39dac42e6c164c84a8021a8d682883",
            "encoding": {
              "codec": "opus",
              "container": "ogg",
              "bitrate": 64000,
              "vbr": true,
              "application": "audio",
              "compression_level": 10
            }
          },
          "fingerprint": "0f831d563c37383b9446ffb565c2e0b6fa5f5ad6df2fefe847ac119cd08faad8",
          "sha256": "ec08bc30d566daff1e6d6b34d7c1209a7a3ae01276a5c07bcc35151b26fd3777",
          "bytes": 39909,
          "duration_seconds": 4.167,
          "voice_profile": "clear_male",
          "reference": "references/german/clear_male.flac"
        },
        {
          "file": "german/random/07.opus",
          "text": "Auf dem Markt wirkten die Tomaten besser organisiert als meine Woche.",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "mode": "clone",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
              "text": "Auf dem Markt wirkten die Tomaten besser organisiert als meine Woche.",
              "language": "German",
              "seed": 8106,
              "ref_text": "Nach dem Regen sah die Straße aus wie ein neuer Anfang. Der Abendwind machte die Stadt ein wenig freundlicher.",
              "xvec_only": false,
              "non_streaming_mode": true
            },
            "model_revision": "fd4b254389122332181a7c3db7f27e918eec64e3",
            "reference_sha256": "a3a94457c71b58c8648d1ead384b746b3847082c40ca6609430f18585d02d5a8",
            "encoding": {
              "codec": "opus",
              "container": "ogg",
              "bitrate": 64000,
              "vbr": true,
              "application": "audio",
              "compression_level": 10
            }
          },
          "fingerprint": "888b160932b18522ec6de15d2dfc5a02e781240a3560d88cbb7de4f40ca3c8e1",
          "sha256": "9e581c5d04b54c1ec909c78d00d8e168ab02037512bcfb08c8f82a55b864f217",
          "bytes": 35194,
          "duration_seconds": 3.926,
          "voice_profile": "relaxed_female",
          "reference": "references/german/relaxed_female.flac"
        },
        {
          "file": "german/random/08.opus",
          "text": "Der Zug hatte Verspätung, also prüften alle sehr ernst ihre Telefone.",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "mode": "clone",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
              "text": "Der Zug hatte Verspätung, also prüften alle sehr ernst ihre Telefone.",
              "language": "German",
              "seed": 8107,
              "ref_text": "Nach dem Regen sah die Straße aus wie ein neuer Anfang. Der Abendwind machte die Stadt ein wenig freundlicher.",
              "xvec_only": false,
              "non_streaming_mode": true
            },
            "model_revision": "fd4b254389122332181a7c3db7f27e918eec64e3",
            "reference_sha256": "f860f47abee5f63b78e84cf54cbbf38150d7ec3a2d970816ed0fcd34a955ea74",
            "encoding": {
              "codec": "opus",
              "container": "ogg",
              "bitrate": 64000,
              "vbr": true,
              "application": "audio",
              "compression_level": 10
            }
          },
          "fingerprint": "a64fdfc41f0877e32cb7df66e7bc15486d570509a4ae78c1a495973c9044772e",
          "sha256": "1026e63f009314d307cffb39e183c4f0df99ce6df85ee7a5dbb102327f805f2d",
          "bytes": 43169,
          "duration_seconds": 4.407,
          "voice_profile": "deep_male",
          "reference": "references/german/deep_male.flac"
        },
        {
          "file": "german/random/09.opus",
          "text": "Ich räumte den Schreibtisch auf und fand einen Stift aus einem alten Plan.",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "mode": "clone",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
              "text": "Ich räumte den Schreibtisch auf und fand einen Stift aus einem alten Plan.",
              "language": "German",
              "seed": 8108,
              "ref_text": "Nach dem Regen sah die Straße aus wie ein neuer Anfang. Der Abendwind machte die Stadt ein wenig freundlicher.",
              "xvec_only": false,
              "non_streaming_mode": true
            },
            "model_revision": "fd4b254389122332181a7c3db7f27e918eec64e3",
            "reference_sha256": "21c715d0237c8970f2eb7a6b14130cfd1a51b9a373976d6e9f852d511c5adb19",
            "encoding": {
              "codec": "opus",
              "container": "ogg",
              "bitrate": 64000,
              "vbr": true,
              "application": "audio",
              "compression_level": 10
            }
          },
          "fingerprint": "38b1afb4699c9d114bb76a3d384ebab600adaf48b7e812d166550d8cc1257878",
          "sha256": "8e3068f748759c051d90712c5c923f843782dbeac4daf1e62dd72d69c1dea60c",
          "bytes": 34709,
          "duration_seconds": 3.687,
          "voice_profile": "cheerful_female",
          "reference": "references/german/cheerful_female.flac"
        },
        {
          "file": "german/random/10.opus",
          "text": "Der Abendwind machte die Stadt ein wenig freundlicher.",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "mode": "clone",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
              "text": "Der Abendwind machte die Stadt ein wenig freundlicher.",
              "language": "German",
              "seed": 8109,
              "ref_text": "Nach dem Regen sah die Straße aus wie ein neuer Anfang. Der Abendwind machte die Stadt ein wenig freundlicher.",
              "xvec_only": false,
              "non_streaming_mode": true
            },
            "model_revision": "fd4b254389122332181a7c3db7f27e918eec64e3",
            "reference_sha256": "b93c5d4fb49985721640a60596bcf4dccf21cda84d1839d2991d1fb1be2611fd",
            "encoding": {
              "codec": "opus",
              "container": "ogg",
              "bitrate": 64000,
              "vbr": true,
              "application": "audio",
              "compression_level": 10
            }
          },
          "fingerprint": "edf33d07429e0579b74cd12ce5b818f4903b4f5093f26d6a4601bd80a82a0922",
          "sha256": "0041cd05da9ed4332ba81e0441997b27206a233a968ee1b2a3a2ec1bc5216443",
          "bytes": 32166,
          "duration_seconds": 3.446,
          "voice_profile": "balanced_male",
          "reference": "references/german/balanced_male.flac"
        }
      ],
      "intro": [
        {
          "file": "german/intro/01.opus",
          "text": "Hallo, hier ist Qwen Studio von Hangry Labs. Wir bauen lokale, einfach startbare Sprachwerkzeuge, damit Menschen privat, offline und in ihrer eigenen Sprache Sprache erzeugen können.",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "mode": "clone",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
              "text": "Hallo, hier ist Qwen Studio von Hangry Labs. Wir bauen lokale, einfach startbare Sprachwerkzeuge, damit Menschen privat, offline und in ihrer eigenen Sprache Sprache erzeugen können.",
              "language": "German",
              "seed": 8500,
              "ref_text": "Nach dem Regen sah die Straße aus wie ein neuer Anfang. Der Abendwind machte die Stadt ein wenig freundlicher.",
              "xvec_only": false,
              "non_streaming_mode": true
            },
            "model_revision": "fd4b254389122332181a7c3db7f27e918eec64e3",
            "reference_sha256": "62f2514f9aaa43b9695c8dc9190d3fbd431ca13ddcb4573e4f7065cb37b3224d",
            "encoding": {
              "codec": "opus",
              "container": "ogg",
              "bitrate": 64000,
              "vbr": true,
              "application": "audio",
              "compression_level": 10
            }
          },
          "fingerprint": "201526fc5a6a28d5eea55ecd1b56aadf9383e757fc5900dfb264d99ab2bac2d5",
          "sha256": "e068e4eed81c8d74dd371565c1b00a6a89b4298732926c6a0cd97174fa94efde",
          "bytes": 110410,
          "duration_seconds": 12.646,
          "voice_profile": "warm_female_narrator",
          "reference": "references/german/warm_female_narrator.flac"
        },
        {
          "file": "german/intro/02.opus",
          "text": "Hallo, hier ist Qwen Studio von Hangry Labs. Wir bauen lokale, einfach startbare Sprachwerkzeuge, damit Menschen privat, offline und in ihrer eigenen Sprache Sprache erzeugen können.",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "mode": "clone",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
              "text": "Hallo, hier ist Qwen Studio von Hangry Labs. Wir bauen lokale, einfach startbare Sprachwerkzeuge, damit Menschen privat, offline und in ihrer eigenen Sprache Sprache erzeugen können.",
              "language": "German",
              "seed": 8501,
              "ref_text": "Nach dem Regen sah die Straße aus wie ein neuer Anfang. Der Abendwind machte die Stadt ein wenig freundlicher.",
              "xvec_only": false,
              "non_streaming_mode": true
            },
            "model_revision": "fd4b254389122332181a7c3db7f27e918eec64e3",
            "reference_sha256": "d57bcf128cf022cdea552927c876c1f283aa3559cf496bf733375c619be7b9b3",
            "encoding": {
              "codec": "opus",
              "container": "ogg",
              "bitrate": 64000,
              "vbr": true,
              "application": "audio",
              "compression_level": 10
            }
          },
          "fingerprint": "94addda8df3335d287a8fdccb167a3a1eebfdf8fad91e57c97b29a2b4e4bf81d",
          "sha256": "8966910d4744767c60cf5264f182d4a6d4711d8574d28071608c9a63709f371d",
          "bytes": 112250,
          "duration_seconds": 11.287,
          "voice_profile": "confident_male",
          "reference": "references/german/confident_male.flac"
        },
        {
          "file": "german/intro/03.opus",
          "text": "Hallo, hier ist Qwen Studio von Hangry Labs. Wir bauen lokale, einfach startbare Sprachwerkzeuge, damit Menschen privat, offline und in ihrer eigenen Sprache Sprache erzeugen können.",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "mode": "clone",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
              "text": "Hallo, hier ist Qwen Studio von Hangry Labs. Wir bauen lokale, einfach startbare Sprachwerkzeuge, damit Menschen privat, offline und in ihrer eigenen Sprache Sprache erzeugen können.",
              "language": "German",
              "seed": 8502,
              "ref_text": "Nach dem Regen sah die Straße aus wie ein neuer Anfang. Der Abendwind machte die Stadt ein wenig freundlicher.",
              "xvec_only": false,
              "non_streaming_mode": true
            },
            "model_revision": "fd4b254389122332181a7c3db7f27e918eec64e3",
            "reference_sha256": "a3a94457c71b58c8648d1ead384b746b3847082c40ca6609430f18585d02d5a8",
            "encoding": {
              "codec": "opus",
              "container": "ogg",
              "bitrate": 64000,
              "vbr": true,
              "application": "audio",
              "compression_level": 10
            }
          },
          "fingerprint": "dd807db043eced5b856471495590e193219bb7205491cf99c2cf0bb0baa23799",
          "sha256": "2160ac7404261053a57118b6b6c3dee6503f6c7c9cdce29d406d462eac1cb2e2",
          "bytes": 101469,
          "duration_seconds": 10.806,
          "voice_profile": "relaxed_female",
          "reference": "references/german/relaxed_female.flac"
        }
      ],
      "clone": [
        {
          "file": "german/clone/01.opus",
          "text": "Hallo, hier ist Qwen Studio von Hangry Labs. Wir bauen lokale, einfach startbare Sprachwerkzeuge, damit Menschen privat, offline und in ihrer eigenen Sprache Sprache erzeugen können.",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "mode": "clone",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
              "text": "Hallo, hier ist Qwen Studio von Hangry Labs. Wir bauen lokale, einfach startbare Sprachwerkzeuge, damit Menschen privat, offline und in ihrer eigenen Sprache Sprache erzeugen können.",
              "language": "German",
              "seed": 8600,
              "ref_text": "The little bookshop was quiet when I arrived. Outside, the rain had stopped, and warm sunlight was finding its way through the windows.",
              "xvec_only": false,
              "non_streaming_mode": true
            },
            "model_revision": "fd4b254389122332181a7c3db7f27e918eec64e3",
            "reference_sha256": "591dc509d7be0360448d36b7a16f4e5bc8587d6096af849ffb37a69a298d7075",
            "encoding": {
              "codec": "opus",
              "container": "ogg",
              "bitrate": 64000,
              "vbr": true,
              "application": "audio",
              "compression_level": 10
            }
          },
          "fingerprint": "e1d7e45c3b1b0daa46461f1632aa0951cfdd521643a5f6a7d9197b001f7413e7",
          "sha256": "b003c3e2291af2e387b4dcb44a0a1d51b6953e7fa54908e1e69bcdac819ccc01",
          "bytes": 101540,
          "duration_seconds": 11.607,
          "voice_profile": "warm_female_narrator",
          "reference": "references/warm_female_narrator.flac"
        }
      ]
    },
    {
      "slug": "french",
      "language": "French",
      "native_name": "Français",
      "icon": "FR",
      "intro_text": "Bonjour, voici Qwen Studio de Hangry Labs. Nous créons des outils vocaux locaux et faciles à lancer pour permettre de produire de la parole en privé, hors ligne et dans sa propre langue.",
      "random": [
        {
          "file": "french/random/01.opus",
          "text": "Le café du matin a négocié ferme, puis il a accepté de m'aider.",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "mode": "clone",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
              "text": "Le café du matin a négocié ferme, puis il a accepté de m'aider.",
              "language": "French",
              "seed": 8100,
              "ref_text": "Après la pluie, la rue semblait recommencer la journée. Le vent du soir a rendu la ville un peu plus douce.",
              "xvec_only": false,
              "non_streaming_mode": true
            },
            "model_revision": "fd4b254389122332181a7c3db7f27e918eec64e3",
            "reference_sha256": "5818fe66d8f782933a08fb088588638f1167024329f79017d85d87d9664d92d2",
            "encoding": {
              "codec": "opus",
              "container": "ogg",
              "bitrate": 64000,
              "vbr": true,
              "application": "audio",
              "compression_level": 10
            }
          },
          "fingerprint": "e49f00b840b83542442b8411d3922a3bafd2f365c82fafab14a322f64d2b8f04",
          "sha256": "a5c7eccd69039584f1ea969da863397d4c1b2deba941373127ebdbab0c1f61dd",
          "bytes": 36106,
          "duration_seconds": 4.167,
          "voice_profile": "warm_female_narrator",
          "reference": "references/french/warm_female_narrator.flac"
        },
        {
          "file": "french/random/02.opus",
          "text": "J'ai rangé mes clés dans un endroit sûr, beaucoup trop sûr.",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "mode": "clone",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
              "text": "J'ai rangé mes clés dans un endroit sûr, beaucoup trop sûr.",
              "language": "French",
              "seed": 8101,
              "ref_text": "Après la pluie, la rue semblait recommencer la journée. Le vent du soir a rendu la ville un peu plus douce.",
              "xvec_only": false,
              "non_streaming_mode": true
            },
            "model_revision": "fd4b254389122332181a7c3db7f27e918eec64e3",
            "reference_sha256": "bce239e649a97d17ee98b16cc8a8e1b78a10337266c8c5ffe72c9fde8a2b9d60",
            "encoding": {
              "codec": "opus",
              "container": "ogg",
              "bitrate": 64000,
              "vbr": true,
              "application": "audio",
              "compression_level": 10
            }
          },
          "fingerprint": "bee854bb613193abe4936486121fd0316a58165bfabb475ba15e6d7f604e1c08",
          "sha256": "b07e2067580aba0539152f1a3265523c3fdd8a0764ff3628d769a3e0487b9da9",
          "bytes": 38041,
          "duration_seconds": 3.446,
          "voice_profile": "calm_male_narrator",
          "reference": "references/french/calm_male_narrator.flac"
        },
        {
          "file": "french/random/03.opus",
          "text": "Après la pluie, la rue semblait recommencer la journée.",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "mode": "clone",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
              "text": "Après la pluie, la rue semblait recommencer la journée.",
              "language": "French",
              "seed": 8102,
              "ref_text": "Après la pluie, la rue semblait recommencer la journée. Le vent du soir a rendu la ville un peu plus douce.",
              "xvec_only": false,
              "non_streaming_mode": true
            },
            "model_revision": "fd4b254389122332181a7c3db7f27e918eec64e3",
            "reference_sha256": "24d68cbc94fb5da76ce0152f99cda901f9b98b70c9af2a293929da919e60aa39",
            "encoding": {
              "codec": "opus",
              "container": "ogg",
              "bitrate": 64000,
              "vbr": true,
              "application": "audio",
              "compression_level": 10
            }
          },
          "fingerprint": "7715e7b30f0cf53026e8869aaacff561ec3e3615b1c46326878d41067dbadc26",
          "sha256": "f7fdd885816a079392ecb25363ebca7b5be7c3ff918877b529db365cff13c4a3",
          "bytes": 26177,
          "duration_seconds": 2.966,
          "voice_profile": "bright_female",
          "reference": "references/french/bright_female.flac"
        },
        {
          "file": "french/random/04.opus",
          "text": "L'odeur de la boulangerie a rendu mon détour parfaitement raisonnable.",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "mode": "clone",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
              "text": "L'odeur de la boulangerie a rendu mon détour parfaitement raisonnable.",
              "language": "French",
              "seed": 8103,
              "ref_text": "Après la pluie, la rue semblait recommencer la journée. Le vent du soir a rendu la ville un peu plus douce.",
              "xvec_only": false,
              "non_streaming_mode": true
            },
            "model_revision": "fd4b254389122332181a7c3db7f27e918eec64e3",
            "reference_sha256": "86cc41f057f27dca6956698379c2c7c2da2e77e5aa60c82a1f100a3fc7492024",
            "encoding": {
              "codec": "opus",
              "container": "ogg",
              "bitrate": 64000,
              "vbr": true,
              "application": "audio",
              "compression_level": 10
            }
          },
          "fingerprint": "4fd496e5631e028982070a9118f01095d0c233633fd5e2664e58ad2bb7f852a2",
          "sha256": "fed377c6047c7a5aa076482ec36b38507d91ddfbc7b79881c2a9f83b82e9bf5a",
          "bytes": 38202,
          "duration_seconds": 3.846,
          "voice_profile": "confident_male",
          "reference": "references/french/confident_male.flac"
        },
        {
          "file": "french/random/05.opus",
          "text": "Mon calendrier plaisante encore; lundi suit toujours dimanche.",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "mode": "clone",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
              "text": "Mon calendrier plaisante encore; lundi suit toujours dimanche.",
              "language": "French",
              "seed": 8104,
              "ref_text": "Après la pluie, la rue semblait recommencer la journée. Le vent du soir a rendu la ville un peu plus douce.",
              "xvec_only": false,
              "non_streaming_mode": true
            },
            "model_revision": "fd4b254389122332181a7c3db7f27e918eec64e3",
            "reference_sha256": "28ece923b32fe38b858ce4a01faf80c81ad15f31d5edba0aab2364c11a7d1aa1",
            "encoding": {
              "codec": "opus",
              "container": "ogg",
              "bitrate": 64000,
              "vbr": true,
              "application": "audio",
              "compression_level": 10
            }
          },
          "fingerprint": "d9c76d9955d69f5ced9c2ace4de2637cf402a9fc99dbe359a6a6e5230c2216da",
          "sha256": "d985d501fafde0e8d33439c6824786eaf9d6080501a97c0699e6abf0774c8e21",
          "bytes": 34540,
          "duration_seconds": 4.087,
          "voice_profile": "gentle_female",
          "reference": "references/french/gentle_female.flac"
        },
        {
          "file": "french/random/06.opus",
          "text": "Je voulais écrire un message court et j'ai produit un petit roman.",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "mode": "clone",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
              "text": "Je voulais écrire un message court et j'ai produit un petit roman.",
              "language": "French",
              "seed": 8105,
              "ref_text": "Après la pluie, la rue semblait recommencer la journée. Le vent du soir a rendu la ville un peu plus douce.",
              "xvec_only": false,
              "non_streaming_mode": true
            },
            "model_revision": "fd4b254389122332181a7c3db7f27e918eec64e3",
            "reference_sha256": "60ac7aa7f0346b9deef86e8bf990e1aa83be3b600b0b108915bf1b46d52ff490",
            "encoding": {
              "codec": "opus",
              "container": "ogg",
              "bitrate": 64000,
              "vbr": true,
              "application": "audio",
              "compression_level": 10
            }
          },
          "fingerprint": "46f8433e8669fc476c1a88737a4c690389312514766ae0d2d54b15ffd32b21b2",
          "sha256": "eb0ca42621b181c9b658d8e7e1b9dd348896d86518f9edce857eb57bf904bf0c",
          "bytes": 28548,
          "duration_seconds": 2.966,
          "voice_profile": "clear_male",
          "reference": "references/french/clear_male.flac"
        },
        {
          "file": "french/random/07.opus",
          "text": "Au marché, les tomates semblaient mieux organisées que ma semaine.",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "mode": "clone",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
              "text": "Au marché, les tomates semblaient mieux organisées que ma semaine.",
              "language": "French",
              "seed": 8106,
              "ref_text": "Après la pluie, la rue semblait recommencer la journée. Le vent du soir a rendu la ville un peu plus douce.",
              "xvec_only": false,
              "non_streaming_mode": true
            },
            "model_revision": "fd4b254389122332181a7c3db7f27e918eec64e3",
            "reference_sha256": "2b0e8b8b3863c7655a83651dd9ec47b1de4bf79774ce1bd8b100b80574c9ae81",
            "encoding": {
              "codec": "opus",
              "container": "ogg",
              "bitrate": 64000,
              "vbr": true,
              "application": "audio",
              "compression_level": 10
            }
          },
          "fingerprint": "1d7b3882fc1619ce0992d7e9d37b39e56f2bbecdb52f79a62ead916a439d780a",
          "sha256": "f3ada978a6073220a5d2854dd39fd3409829f81b6e5086a84842ca0663c0de25",
          "bytes": 34714,
          "duration_seconds": 4.327,
          "voice_profile": "relaxed_female",
          "reference": "references/french/relaxed_female.flac"
        },
        {
          "file": "french/random/08.opus",
          "text": "Le train avait du retard, alors chacun a étudié son téléphone avec sérieux.",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "mode": "clone",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
              "text": "Le train avait du retard, alors chacun a étudié son téléphone avec sérieux.",
              "language": "French",
              "seed": 8107,
              "ref_text": "Après la pluie, la rue semblait recommencer la journée. Le vent du soir a rendu la ville un peu plus douce.",
              "xvec_only": false,
              "non_streaming_mode": true
            },
            "model_revision": "fd4b254389122332181a7c3db7f27e918eec64e3",
            "reference_sha256": "8bc971a28bb0671d1224bfd10db9e1ca1fc8477b0ea8cc45dc1d7abf3c022470",
            "encoding": {
              "codec": "opus",
              "container": "ogg",
              "bitrate": 64000,
              "vbr": true,
              "application": "audio",
              "compression_level": 10
            }
          },
          "fingerprint": "1ae0154242f9cb5a82709e67f6e45c590044f44dca490e55ab742fcb6e0408b6",
          "sha256": "3915c07d44139f92143d22d94c44f29b2a2dff3dc3ee3f03054270ab1a764a3b",
          "bytes": 43502,
          "duration_seconds": 4.327,
          "voice_profile": "deep_male",
          "reference": "references/french/deep_male.flac"
        },
        {
          "file": "french/random/09.opus",
          "text": "J'ai rangé mon bureau et trouvé un stylo venu d'un ancien projet.",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "mode": "clone",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
              "text": "J'ai rangé mon bureau et trouvé un stylo venu d'un ancien projet.",
              "language": "French",
              "seed": 8108,
              "ref_text": "Après la pluie, la rue semblait recommencer la journée. Le vent du soir a rendu la ville un peu plus douce.",
              "xvec_only": false,
              "non_streaming_mode": true
            },
            "model_revision": "fd4b254389122332181a7c3db7f27e918eec64e3",
            "reference_sha256": "71ae5f7ca01966ea1016ecd4466707dc500cfaca6e8b1d6b83e45e8341bce6ae",
            "encoding": {
              "codec": "opus",
              "container": "ogg",
              "bitrate": 64000,
              "vbr": true,
              "application": "audio",
              "compression_level": 10
            }
          },
          "fingerprint": "9e3be117724dae38b65bf7b3224e892944501db7657e30e2e0f9c04248bd762c",
          "sha256": "4e0e29f7179ebf09fe9c46e7d8aa880b91da90a43909ae541d496cd90b97bed4",
          "bytes": 30050,
          "duration_seconds": 3.446,
          "voice_profile": "cheerful_female",
          "reference": "references/french/cheerful_female.flac"
        },
        {
          "file": "french/random/10.opus",
          "text": "Le vent du soir a rendu la ville un peu plus douce.",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "mode": "clone",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
              "text": "Le vent du soir a rendu la ville un peu plus douce.",
              "language": "French",
              "seed": 8109,
              "ref_text": "Après la pluie, la rue semblait recommencer la journée. Le vent du soir a rendu la ville un peu plus douce.",
              "xvec_only": false,
              "non_streaming_mode": true
            },
            "model_revision": "fd4b254389122332181a7c3db7f27e918eec64e3",
            "reference_sha256": "6f1f57473fdf3ae7ae826e13af4a6db3ed74f919e269436a394ccb39a17c174c",
            "encoding": {
              "codec": "opus",
              "container": "ogg",
              "bitrate": 64000,
              "vbr": true,
              "application": "audio",
              "compression_level": 10
            }
          },
          "fingerprint": "7a8407246389c88964be3a2cbbb8cb6aa7a9d34b127de1c178dbeb5611705361",
          "sha256": "50a48289bed4acc997710b0554949a8721a778eb129452bb33429506b823b98b",
          "bytes": 27001,
          "duration_seconds": 2.886,
          "voice_profile": "balanced_male",
          "reference": "references/french/balanced_male.flac"
        }
      ],
      "intro": [
        {
          "file": "french/intro/01.opus",
          "text": "Bonjour, voici Qwen Studio de Hangry Labs. Nous créons des outils vocaux locaux et faciles à lancer pour permettre de produire de la parole en privé, hors ligne et dans sa propre langue.",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "mode": "clone",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
              "text": "Bonjour, voici Qwen Studio de Hangry Labs. Nous créons des outils vocaux locaux et faciles à lancer pour permettre de produire de la parole en privé, hors ligne et dans sa propre langue.",
              "language": "French",
              "seed": 8500,
              "ref_text": "Après la pluie, la rue semblait recommencer la journée. Le vent du soir a rendu la ville un peu plus douce.",
              "xvec_only": false,
              "non_streaming_mode": true
            },
            "model_revision": "fd4b254389122332181a7c3db7f27e918eec64e3",
            "reference_sha256": "5818fe66d8f782933a08fb088588638f1167024329f79017d85d87d9664d92d2",
            "encoding": {
              "codec": "opus",
              "container": "ogg",
              "bitrate": 64000,
              "vbr": true,
              "application": "audio",
              "compression_level": 10
            }
          },
          "fingerprint": "f80f6951b07f370287b8c8191930262d9bc274fdc8e4772456f3bbfe1907d5e0",
          "sha256": "bc4827043c180183eac6d4b57afda5658c19a89746774b4a7405b1c57541967d",
          "bytes": 94400,
          "duration_seconds": 11.046,
          "voice_profile": "warm_female_narrator",
          "reference": "references/french/warm_female_narrator.flac"
        },
        {
          "file": "french/intro/02.opus",
          "text": "Bonjour, voici Qwen Studio de Hangry Labs. Nous créons des outils vocaux locaux et faciles à lancer pour permettre de produire de la parole en privé, hors ligne et dans sa propre langue.",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "mode": "clone",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
              "text": "Bonjour, voici Qwen Studio de Hangry Labs. Nous créons des outils vocaux locaux et faciles à lancer pour permettre de produire de la parole en privé, hors ligne et dans sa propre langue.",
              "language": "French",
              "seed": 8501,
              "ref_text": "Après la pluie, la rue semblait recommencer la journée. Le vent du soir a rendu la ville un peu plus douce.",
              "xvec_only": false,
              "non_streaming_mode": true
            },
            "model_revision": "fd4b254389122332181a7c3db7f27e918eec64e3",
            "reference_sha256": "86cc41f057f27dca6956698379c2c7c2da2e77e5aa60c82a1f100a3fc7492024",
            "encoding": {
              "codec": "opus",
              "container": "ogg",
              "bitrate": 64000,
              "vbr": true,
              "application": "audio",
              "compression_level": 10
            }
          },
          "fingerprint": "96080d789697e0a31e200b571b2c8c47a974e9dfe2fdddb38cd181da5602a647",
          "sha256": "b964befa246e7f6b0bf5ad8a2a3e9c00f0ef1a7309550d3320e23272f3def2a6",
          "bytes": 91191,
          "duration_seconds": 9.687,
          "voice_profile": "confident_male",
          "reference": "references/french/confident_male.flac"
        },
        {
          "file": "french/intro/03.opus",
          "text": "Bonjour, voici Qwen Studio de Hangry Labs. Nous créons des outils vocaux locaux et faciles à lancer pour permettre de produire de la parole en privé, hors ligne et dans sa propre langue.",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "mode": "clone",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
              "text": "Bonjour, voici Qwen Studio de Hangry Labs. Nous créons des outils vocaux locaux et faciles à lancer pour permettre de produire de la parole en privé, hors ligne et dans sa propre langue.",
              "language": "French",
              "seed": 8502,
              "ref_text": "Après la pluie, la rue semblait recommencer la journée. Le vent du soir a rendu la ville un peu plus douce.",
              "xvec_only": false,
              "non_streaming_mode": true
            },
            "model_revision": "fd4b254389122332181a7c3db7f27e918eec64e3",
            "reference_sha256": "2b0e8b8b3863c7655a83651dd9ec47b1de4bf79774ce1bd8b100b80574c9ae81",
            "encoding": {
              "codec": "opus",
              "container": "ogg",
              "bitrate": 64000,
              "vbr": true,
              "application": "audio",
              "compression_level": 10
            }
          },
          "fingerprint": "c5de7a72d216e4259415f7d883c932349df6f23662c7560ef9011c8267072233",
          "sha256": "678fd636ed99e367bed0f93c6c211a0a425bdae9ff12329c1e35a614d8ad34d0",
          "bytes": 92435,
          "duration_seconds": 10.726,
          "voice_profile": "relaxed_female",
          "reference": "references/french/relaxed_female.flac"
        }
      ],
      "clone": [
        {
          "file": "french/clone/01.opus",
          "text": "Bonjour, voici Qwen Studio de Hangry Labs. Nous créons des outils vocaux locaux et faciles à lancer pour permettre de produire de la parole en privé, hors ligne et dans sa propre langue.",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "mode": "clone",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
              "text": "Bonjour, voici Qwen Studio de Hangry Labs. Nous créons des outils vocaux locaux et faciles à lancer pour permettre de produire de la parole en privé, hors ligne et dans sa propre langue.",
              "language": "French",
              "seed": 8600,
              "ref_text": "The little bookshop was quiet when I arrived. Outside, the rain had stopped, and warm sunlight was finding its way through the windows.",
              "xvec_only": false,
              "non_streaming_mode": true
            },
            "model_revision": "fd4b254389122332181a7c3db7f27e918eec64e3",
            "reference_sha256": "591dc509d7be0360448d36b7a16f4e5bc8587d6096af849ffb37a69a298d7075",
            "encoding": {
              "codec": "opus",
              "container": "ogg",
              "bitrate": 64000,
              "vbr": true,
              "application": "audio",
              "compression_level": 10
            }
          },
          "fingerprint": "119fd20c91988318753d9e56f739caf8fed06ca2e58f3d6e825e7673c1b24c17",
          "sha256": "6905e0166f0c7ab7f37c309fe041a08f294f44224bc709288046adaa6cf2a1ac",
          "bytes": 109401,
          "duration_seconds": 12.406,
          "voice_profile": "warm_female_narrator",
          "reference": "references/warm_female_narrator.flac"
        }
      ]
    },
    {
      "slug": "russian",
      "language": "Russian",
      "native_name": "Русский",
      "icon": "RU",
      "intro_text": "Здравствуйте, это Qwen Studio от Hangry Labs. Мы создаем локальные и простые в запуске голосовые инструменты, чтобы люди могли создавать речь приватно, офлайн и на своем языке.",
      "random": [
        {
          "file": "russian/random/01.opus",
          "text": "Утренний кофе долго торговался, но в итоге согласился помочь.",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "mode": "clone",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
              "text": "Утренний кофе долго торговался, но в итоге согласился помочь.",
              "language": "Russian",
              "seed": 8100,
              "ref_text": "После дождя улица выглядела как новое начало. Вечерний ветер сделал город немного спокойнее.",
              "xvec_only": false,
              "non_streaming_mode": true
            },
            "model_revision": "fd4b254389122332181a7c3db7f27e918eec64e3",
            "reference_sha256": "441147203cee79ec1c438aedf32696f8de4c1e266e1c6ca3fefd9641d80d4cbf",
            "encoding": {
              "codec": "opus",
              "container": "ogg",
              "bitrate": 64000,
              "vbr": true,
              "application": "audio",
              "compression_level": 10
            }
          },
          "fingerprint": "7e4f844372b88a0b2524c0ca501e7c4491dad878497e2999cd4b33a446bc32ff",
          "sha256": "70fe0832013d41ecfb127191e5f703a04f34625e8c3e1e43cea199eaf0c72633",
          "bytes": 39679,
          "duration_seconds": 4.487,
          "voice_profile": "warm_female_narrator",
          "reference": "references/russian/warm_female_narrator.flac"
        },
        {
          "file": "russian/random/02.opus",
          "text": "Я положил ключи в надежное место, кажется, слишком надежное.",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "mode": "clone",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
              "text": "Я положил ключи в надежное место, кажется, слишком надежное.",
              "language": "Russian",
              "seed": 8101,
              "ref_text": "После дождя улица выглядела как новое начало. Вечерний ветер сделал город немного спокойнее.",
              "xvec_only": false,
              "non_streaming_mode": true
            },
            "model_revision": "fd4b254389122332181a7c3db7f27e918eec64e3",
            "reference_sha256": "4233ff17ed54096b005774825ffefcfe79670d679e97fda7ae54ec73bc5ec5ef",
            "encoding": {
              "codec": "opus",
              "container": "ogg",
              "bitrate": 64000,
              "vbr": true,
              "application": "audio",
              "compression_level": 10
            }
          },
          "fingerprint": "a40c6ab512275bd329bd9c87ea51412ffde0d684291ada0c735b2daed92a209c",
          "sha256": "1a492ab6805d739f12d0a958e1a9b22acc3a3147d61cd59eb36ab44f423cc44d",
          "bytes": 43130,
          "duration_seconds": 4.646,
          "voice_profile": "calm_male_narrator",
          "reference": "references/russian/calm_male_narrator.flac"
        },
        {
          "file": "russian/random/03.opus",
          "text": "После дождя улица выглядела как новое начало.",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "mode": "clone",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
              "text": "После дождя улица выглядела как новое начало.",
              "language": "Russian",
              "seed": 8102,
              "ref_text": "После дождя улица выглядела как новое начало. Вечерний ветер сделал город немного спокойнее.",
              "xvec_only": false,
              "non_streaming_mode": true
            },
            "model_revision": "fd4b254389122332181a7c3db7f27e918eec64e3",
            "reference_sha256": "b24ad00ecd4c5c79a69f413e24d613e06558d54625373456cd965908bfc77c08",
            "encoding": {
              "codec": "opus",
              "container": "ogg",
              "bitrate": 64000,
              "vbr": true,
              "application": "audio",
              "compression_level": 10
            }
          },
          "fingerprint": "11023b2d9050479713eca4d617f09f6574f2a91c6df7a5233adfd976dfe6c036",
          "sha256": "2f92245403ec95761dd0d76af8002ae785704a68ea1519214b644d0af6262b0a",
          "bytes": 35773,
          "duration_seconds": 3.926,
          "voice_profile": "bright_female",
          "reference": "references/russian/bright_female.flac"
        },
        {
          "file": "russian/random/04.opus",
          "text": "Запах пекарни сделал обходной путь совершенно разумным.",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "mode": "clone",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
              "text": "Запах пекарни сделал обходной путь совершенно разумным.",
              "language": "Russian",
              "seed": 8103,
              "ref_text": "После дождя улица выглядела как новое начало. Вечерний ветер сделал город немного спокойнее.",
              "xvec_only": false,
              "non_streaming_mode": true
            },
            "model_revision": "fd4b254389122332181a7c3db7f27e918eec64e3",
            "reference_sha256": "2f18f8cfebfeb5ec2f48141b942a357c62bcad1436ad9a1338194a95af383ff8",
            "encoding": {
              "codec": "opus",
              "container": "ogg",
              "bitrate": 64000,
              "vbr": true,
              "application": "audio",
              "compression_level": 10
            }
          },
          "fingerprint": "2e0e39e6ad04a07b023e38849c3a43871f2ad219cc402db60636aa5241a50603",
          "sha256": "09c6f5bc2ff1534edec71d2ab2f73c1180039ca632e724a5ebb5657397ee4d69",
          "bytes": 36674,
          "duration_seconds": 3.846,
          "voice_profile": "confident_male",
          "reference": "references/russian/confident_male.flac"
        },
        {
          "file": "russian/random/05.opus",
          "text": "У моего календаря есть чувство юмора: понедельник снова после воскресенья.",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "mode": "clone",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
              "text": "У моего календаря есть чувство юмора: понедельник снова после воскресенья.",
              "language": "Russian",
              "seed": 8104,
              "ref_text": "После дождя улица выглядела как новое начало. Вечерний ветер сделал город немного спокойнее.",
              "xvec_only": false,
              "non_streaming_mode": true
            },
            "model_revision": "fd4b254389122332181a7c3db7f27e918eec64e3",
            "reference_sha256": "28904b9956b7b318f31ac7617a40c7f2b527f0960b2cb989a6b861ccf3d64086",
            "encoding": {
              "codec": "opus",
              "container": "ogg",
              "bitrate": 64000,
              "vbr": true,
              "application": "audio",
              "compression_level": 10
            }
          },
          "fingerprint": "752fc55de5f3b735d411414f965b2e74d4dbaef1b18bc914407bb561f268fd2a",
          "sha256": "1bb0553d63127e18562e285ac78a377c6382fd83d2b64b82d5abd1a72e81e1e3",
          "bytes": 50166,
          "duration_seconds": 5.686,
          "voice_profile": "gentle_female",
          "reference": "references/russian/gentle_female.flac"
        },
        {
          "file": "russian/random/06.opus",
          "text": "Я хотел написать короткое сообщение, а получился маленький рассказ.",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "mode": "clone",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
              "text": "Я хотел написать короткое сообщение, а получился маленький рассказ.",
              "language": "Russian",
              "seed": 8105,
              "ref_text": "После дождя улица выглядела как новое начало. Вечерний ветер сделал город немного спокойнее.",
              "xvec_only": false,
              "non_streaming_mode": true
            },
            "model_revision": "fd4b254389122332181a7c3db7f27e918eec64e3",
            "reference_sha256": "e896a56ed3696a67fc491120da5284daff20830aecbc417e470136e19535a044",
            "encoding": {
              "codec": "opus",
              "container": "ogg",
              "bitrate": 64000,
              "vbr": true,
              "application": "audio",
              "compression_level": 10
            }
          },
          "fingerprint": "4f4ad1792efa5586385ef55c387cd8703f6340d86a1c11dd9e1c54a28e7e3dee",
          "sha256": "f68630d4a987256a4e146d0bb024d7723193b364a5a4212b917ed0809eeada15",
          "bytes": 37788,
          "duration_seconds": 4.006,
          "voice_profile": "clear_male",
          "reference": "references/russian/clear_male.flac"
        },
        {
          "file": "russian/random/07.opus",
          "text": "На рынке помидоры выглядели организованнее моей недели.",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "mode": "clone",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
              "text": "На рынке помидоры выглядели организованнее моей недели.",
              "language": "Russian",
              "seed": 8106,
              "ref_text": "После дождя улица выглядела как новое начало. Вечерний ветер сделал город немного спокойнее.",
              "xvec_only": false,
              "non_streaming_mode": true
            },
            "model_revision": "fd4b254389122332181a7c3db7f27e918eec64e3",
            "reference_sha256": "645553d8edce8bf61af488e5ffbad2e38cb637670663c9b9914839b259c1f8d9",
            "encoding": {
              "codec": "opus",
              "container": "ogg",
              "bitrate": 64000,
              "vbr": true,
              "application": "audio",
              "compression_level": 10
            }
          },
          "fingerprint": "8ed5b16b5befc23cafba8ef1d44317a3458f7e700a12fff0b47841239452545f",
          "sha256": "44ed88e808c9985017047c2a5524bb2006ecdc921dd8864f2dbe87981a87d8c9",
          "bytes": 30992,
          "duration_seconds": 3.607,
          "voice_profile": "relaxed_female",
          "reference": "references/russian/relaxed_female.flac"
        },
        {
          "file": "russian/random/08.opus",
          "text": "Поезд задержался, и все серьезно изучали свои телефоны.",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "mode": "clone",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
              "text": "Поезд задержался, и все серьезно изучали свои телефоны.",
              "language": "Russian",
              "seed": 8107,
              "ref_text": "После дождя улица выглядела как новое начало. Вечерний ветер сделал город немного спокойнее.",
              "xvec_only": false,
              "non_streaming_mode": true
            },
            "model_revision": "fd4b254389122332181a7c3db7f27e918eec64e3",
            "reference_sha256": "7253ea073dd54cc80fca1f09dc51605c356c6c1f3ae42e64b680facd2bbd0e95",
            "encoding": {
              "codec": "opus",
              "container": "ogg",
              "bitrate": 64000,
              "vbr": true,
              "application": "audio",
              "compression_level": 10
            }
          },
          "fingerprint": "039ba07e5b6e97df025adc78886ee5a12f9bca4d5f5f1b4c3b1d07b986244447",
          "sha256": "5f17bb1c170bb3d2982961e88d8aac18cbe3752d592008836eeae207fefe875a",
          "bytes": 39541,
          "duration_seconds": 4.247,
          "voice_profile": "deep_male",
          "reference": "references/russian/deep_male.flac"
        },
        {
          "file": "russian/random/09.opus",
          "text": "Я убрал стол и нашел ручку из старого плана.",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "mode": "clone",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
              "text": "Я убрал стол и нашел ручку из старого плана.",
              "language": "Russian",
              "seed": 8108,
              "ref_text": "После дождя улица выглядела как новое начало. Вечерний ветер сделал город немного спокойнее.",
              "xvec_only": false,
              "non_streaming_mode": true
            },
            "model_revision": "fd4b254389122332181a7c3db7f27e918eec64e3",
            "reference_sha256": "2bac98e29afda2f0610f67db69ba1cce9870ec79fc59953107b484604f955ef6",
            "encoding": {
              "codec": "opus",
              "container": "ogg",
              "bitrate": 64000,
              "vbr": true,
              "application": "audio",
              "compression_level": 10
            }
          },
          "fingerprint": "0510c6b7a1253e2a177a61ba4764bad42a321214dcb706adb52ca7719d087f7f",
          "sha256": "6b1dfd4ad78955080be02d282fbcf999f59faf3607ab036a8ca87a81b9e7460f",
          "bytes": 29721,
          "duration_seconds": 3.366,
          "voice_profile": "cheerful_female",
          "reference": "references/russian/cheerful_female.flac"
        },
        {
          "file": "russian/random/10.opus",
          "text": "Вечерний ветер сделал город немного спокойнее.",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "mode": "clone",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
              "text": "Вечерний ветер сделал город немного спокойнее.",
              "language": "Russian",
              "seed": 8109,
              "ref_text": "После дождя улица выглядела как новое начало. Вечерний ветер сделал город немного спокойнее.",
              "xvec_only": false,
              "non_streaming_mode": true
            },
            "model_revision": "fd4b254389122332181a7c3db7f27e918eec64e3",
            "reference_sha256": "980210ee85d2b504acb80106d8864df2a0583a691a67068516c56684c97a9163",
            "encoding": {
              "codec": "opus",
              "container": "ogg",
              "bitrate": 64000,
              "vbr": true,
              "application": "audio",
              "compression_level": 10
            }
          },
          "fingerprint": "c0c08dd9648054de93df1b81f6280b5106e92ee2d627b98d48b463a7af6d7a0d",
          "sha256": "e063272ad155737d5f42fda381830915c18411fdcfa3ec5b526e7276bfa1ba0f",
          "bytes": 25545,
          "duration_seconds": 2.567,
          "voice_profile": "balanced_male",
          "reference": "references/russian/balanced_male.flac"
        }
      ],
      "intro": [
        {
          "file": "russian/intro/01.opus",
          "text": "Здравствуйте, это Qwen Studio от Hangry Labs. Мы создаем локальные и простые в запуске голосовые инструменты, чтобы люди могли создавать речь приватно, офлайн и на своем языке.",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "mode": "clone",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
              "text": "Здравствуйте, это Qwen Studio от Hangry Labs. Мы создаем локальные и простые в запуске голосовые инструменты, чтобы люди могли создавать речь приватно, офлайн и на своем языке.",
              "language": "Russian",
              "seed": 8500,
              "ref_text": "После дождя улица выглядела как новое начало. Вечерний ветер сделал город немного спокойнее.",
              "xvec_only": false,
              "non_streaming_mode": true
            },
            "model_revision": "fd4b254389122332181a7c3db7f27e918eec64e3",
            "reference_sha256": "441147203cee79ec1c438aedf32696f8de4c1e266e1c6ca3fefd9641d80d4cbf",
            "encoding": {
              "codec": "opus",
              "container": "ogg",
              "bitrate": 64000,
              "vbr": true,
              "application": "audio",
              "compression_level": 10
            }
          },
          "fingerprint": "31a49e4cf5da4208136b05c4c2f1adc5ac07df14a4a56d1f6c8a43dcf37f99b0",
          "sha256": "167824e23774c769a84ee3a1480747d55dec000b73446a2466961e9fee8b0e8b",
          "bytes": 114845,
          "duration_seconds": 12.886,
          "voice_profile": "warm_female_narrator",
          "reference": "references/russian/warm_female_narrator.flac"
        },
        {
          "file": "russian/intro/02.opus",
          "text": "Здравствуйте, это Qwen Studio от Hangry Labs. Мы создаем локальные и простые в запуске голосовые инструменты, чтобы люди могли создавать речь приватно, офлайн и на своем языке.",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "mode": "clone",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
              "text": "Здравствуйте, это Qwen Studio от Hangry Labs. Мы создаем локальные и простые в запуске голосовые инструменты, чтобы люди могли создавать речь приватно, офлайн и на своем языке.",
              "language": "Russian",
              "seed": 8501,
              "ref_text": "После дождя улица выглядела как новое начало. Вечерний ветер сделал город немного спокойнее.",
              "xvec_only": false,
              "non_streaming_mode": true
            },
            "model_revision": "fd4b254389122332181a7c3db7f27e918eec64e3",
            "reference_sha256": "2f18f8cfebfeb5ec2f48141b942a357c62bcad1436ad9a1338194a95af383ff8",
            "encoding": {
              "codec": "opus",
              "container": "ogg",
              "bitrate": 64000,
              "vbr": true,
              "application": "audio",
              "compression_level": 10
            }
          },
          "fingerprint": "5bbf5fba8704f7c20b2fb4f2292e0063a55c73f5a357ffe04f2bfd8facaea8ea",
          "sha256": "efef633af608531bedbedc7bb3d2a1ad4d8ea406125ad0a00465537d49209a8e",
          "bytes": 108788,
          "duration_seconds": 11.607,
          "voice_profile": "confident_male",
          "reference": "references/russian/confident_male.flac"
        },
        {
          "file": "russian/intro/03.opus",
          "text": "Здравствуйте, это Qwen Studio от Hangry Labs. Мы создаем локальные и простые в запуске голосовые инструменты, чтобы люди могли создавать речь приватно, офлайн и на своем языке.",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "mode": "clone",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
              "text": "Здравствуйте, это Qwen Studio от Hangry Labs. Мы создаем локальные и простые в запуске голосовые инструменты, чтобы люди могли создавать речь приватно, офлайн и на своем языке.",
              "language": "Russian",
              "seed": 8502,
              "ref_text": "После дождя улица выглядела как новое начало. Вечерний ветер сделал город немного спокойнее.",
              "xvec_only": false,
              "non_streaming_mode": true
            },
            "model_revision": "fd4b254389122332181a7c3db7f27e918eec64e3",
            "reference_sha256": "645553d8edce8bf61af488e5ffbad2e38cb637670663c9b9914839b259c1f8d9",
            "encoding": {
              "codec": "opus",
              "container": "ogg",
              "bitrate": 64000,
              "vbr": true,
              "application": "audio",
              "compression_level": 10
            }
          },
          "fingerprint": "9fe882460d1d9ef254509ad61ebd4330236a9f03214e59fab4c0216222680c9a",
          "sha256": "56a0bbe499aab243853f19ea9aa76a38a33d3df58ebcf8e2ed9d8f29d6a56899",
          "bytes": 107475,
          "duration_seconds": 12.166,
          "voice_profile": "relaxed_female",
          "reference": "references/russian/relaxed_female.flac"
        }
      ],
      "clone": [
        {
          "file": "russian/clone/01.opus",
          "text": "Здравствуйте, это Qwen Studio от Hangry Labs. Мы создаем локальные и простые в запуске голосовые инструменты, чтобы люди могли создавать речь приватно, офлайн и на своем языке.",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "mode": "clone",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
              "text": "Здравствуйте, это Qwen Studio от Hangry Labs. Мы создаем локальные и простые в запуске голосовые инструменты, чтобы люди могли создавать речь приватно, офлайн и на своем языке.",
              "language": "Russian",
              "seed": 8600,
              "ref_text": "The little bookshop was quiet when I arrived. Outside, the rain had stopped, and warm sunlight was finding its way through the windows.",
              "xvec_only": false,
              "non_streaming_mode": true
            },
            "model_revision": "fd4b254389122332181a7c3db7f27e918eec64e3",
            "reference_sha256": "591dc509d7be0360448d36b7a16f4e5bc8587d6096af849ffb37a69a298d7075",
            "encoding": {
              "codec": "opus",
              "container": "ogg",
              "bitrate": 64000,
              "vbr": true,
              "application": "audio",
              "compression_level": 10
            }
          },
          "fingerprint": "2a4a71883da791eed406119984cc277b40b339dde655cd131d6c53a1841d743b",
          "sha256": "e868ec885ad5bbe2e28cadc2fe90a7841b98c1a2e9285d9a4be8cb6671dc2234",
          "bytes": 109391,
          "duration_seconds": 12.007,
          "voice_profile": "warm_female_narrator",
          "reference": "references/warm_female_narrator.flac"
        }
      ]
    },
    {
      "slug": "portuguese",
      "language": "Portuguese",
      "native_name": "Português",
      "icon": "PT",
      "intro_text": "Olá, este é o Qwen Studio da Hangry Labs. Criamos ferramentas de voz locais e fáceis de executar para que as pessoas possam gerar fala com privacidade, offline e no próprio idioma.",
      "random": [
        {
          "file": "portuguese/random/01.opus",
          "text": "O café da manhã negociou bastante, mas acabou ajudando.",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "mode": "clone",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
              "text": "O café da manhã negociou bastante, mas acabou ajudando.",
              "language": "Portuguese",
              "seed": 8100,
              "ref_text": "Depois da chuva, a rua parecia um novo começo. O vento da tarde deixou a cidade um pouco mais calma.",
              "xvec_only": false,
              "non_streaming_mode": true
            },
            "model_revision": "fd4b254389122332181a7c3db7f27e918eec64e3",
            "reference_sha256": "76fa1c7387e61798edc751a02f74763dbd4498673e02458085a9c1f126d6c050",
            "encoding": {
              "codec": "opus",
              "container": "ogg",
              "bitrate": 64000,
              "vbr": true,
              "application": "audio",
              "compression_level": 10
            }
          },
          "fingerprint": "39786598d0f0b823f25c4078be408803e11d02745dcb5931e5d15b458067140d",
          "sha256": "1c2c1dd7535a0dde5b55751d7c23aae825c65455273bef3211aee7ba2ff782aa",
          "bytes": 30366,
          "duration_seconds": 3.926,
          "voice_profile": "warm_female_narrator",
          "reference": "references/portuguese/warm_female_narrator.flac"
        },
        {
          "file": "portuguese/random/02.opus",
          "text": "Guardei as chaves em um lugar seguro, seguro demais.",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "mode": "clone",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
              "text": "Guardei as chaves em um lugar seguro, seguro demais.",
              "language": "Portuguese",
              "seed": 8101,
              "ref_text": "Depois da chuva, a rua parecia um novo começo. O vento da tarde deixou a cidade um pouco mais calma.",
              "xvec_only": false,
              "non_streaming_mode": true
            },
            "model_revision": "fd4b254389122332181a7c3db7f27e918eec64e3",
            "reference_sha256": "59fc5b42df9f5e4d4ac9597ca066d058be67152950e942ad3b895e2c804236bb",
            "encoding": {
              "codec": "opus",
              "container": "ogg",
              "bitrate": 64000,
              "vbr": true,
              "application": "audio",
              "compression_level": 10
            }
          },
          "fingerprint": "76ccdf70acbc3ec70791dfd9aba1a6e82b24ed4f5d659eb24ed5ccc723ee10f4",
          "sha256": "e8dbccbfd1a602ddf2928e33ebc5150e5ab362102f589639e82f87cc57c5a9fb",
          "bytes": 29029,
          "duration_seconds": 3.607,
          "voice_profile": "calm_male_narrator",
          "reference": "references/portuguese/calm_male_narrator.flac"
        },
        {
          "file": "portuguese/random/03.opus",
          "text": "Depois da chuva, a rua parecia um novo começo.",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "mode": "clone",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
              "text": "Depois da chuva, a rua parecia um novo começo.",
              "language": "Portuguese",
              "seed": 8102,
              "ref_text": "Depois da chuva, a rua parecia um novo começo. O vento da tarde deixou a cidade um pouco mais calma.",
              "xvec_only": false,
              "non_streaming_mode": true
            },
            "model_revision": "fd4b254389122332181a7c3db7f27e918eec64e3",
            "reference_sha256": "758b21032a98887f7b6b544c3c30fceaaf6fa102f8912cddcc533265e128620d",
            "encoding": {
              "codec": "opus",
              "container": "ogg",
              "bitrate": 64000,
              "vbr": true,
              "application": "audio",
              "compression_level": 10
            }
          },
          "fingerprint": "cfd3d24c9268338d4b66b2ecbd5e1c0c2094a7244d1e010ace432f7839f32895",
          "sha256": "e0f4e7bec8a4dcdb4a95128461024f1eac1aca06444664243f49e8f161e17195",
          "bytes": 27492,
          "duration_seconds": 3.687,
          "voice_profile": "bright_female",
          "reference": "references/portuguese/bright_female.flac"
        },
        {
          "file": "portuguese/random/04.opus",
          "text": "O cheiro da padaria tornou o desvio totalmente razoável.",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "mode": "clone",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
              "text": "O cheiro da padaria tornou o desvio totalmente razoável.",
              "language": "Portuguese",
              "seed": 8103,
              "ref_text": "Depois da chuva, a rua parecia um novo começo. O vento da tarde deixou a cidade um pouco mais calma.",
              "xvec_only": false,
              "non_streaming_mode": true
            },
            "model_revision": "fd4b254389122332181a7c3db7f27e918eec64e3",
            "reference_sha256": "e0b5cdf177a132ceb477c9e474ea70fa6626c39672bc27d20f5653f62110a1ba",
            "encoding": {
              "codec": "opus",
              "container": "ogg",
              "bitrate": 64000,
              "vbr": true,
              "application": "audio",
              "compression_level": 10
            }
          },
          "fingerprint": "2680e967b69184d544471a7765ace807651aa726477630f27ec1841ca1b39efa",
          "sha256": "b8d8d2556abc634ded9514ff6086a76b29e75972de3f1fd6c6312a44d50b81a6",
          "bytes": 28277,
          "duration_seconds": 3.526,
          "voice_profile": "confident_male",
          "reference": "references/portuguese/confident_male.flac"
        },
        {
          "file": "portuguese/random/05.opus",
          "text": "Meu calendário tem humor; segunda-feira veio de novo depois de domingo.",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "mode": "clone",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
              "text": "Meu calendário tem humor; segunda-feira veio de novo depois de domingo.",
              "language": "Portuguese",
              "seed": 8104,
              "ref_text": "Depois da chuva, a rua parecia um novo começo. O vento da tarde deixou a cidade um pouco mais calma.",
              "xvec_only": false,
              "non_streaming_mode": true
            },
            "model_revision": "fd4b254389122332181a7c3db7f27e918eec64e3",
            "reference_sha256": "4f43eb6f29ece903df78b959c90d73405d5fa3583ca9329aaceca720097ec35c",
            "encoding": {
              "codec": "opus",
              "container": "ogg",
              "bitrate": 64000,
              "vbr": true,
              "application": "audio",
              "compression_level": 10
            }
          },
          "fingerprint": "857b1ba747521dec991d11ed0668adb9caba914f3b161fb23e70e5c56820ebe4",
          "sha256": "884d5b31f6e882492777d37a5071b3280a5a5a035daaa5783cb472c0fab9be8f",
          "bytes": 36743,
          "duration_seconds": 4.886,
          "voice_profile": "gentle_female",
          "reference": "references/portuguese/gentle_female.flac"
        },
        {
          "file": "portuguese/random/06.opus",
          "text": "Eu queria escrever uma mensagem curta e saiu uma pequena história.",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "mode": "clone",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
              "text": "Eu queria escrever uma mensagem curta e saiu uma pequena história.",
              "language": "Portuguese",
              "seed": 8105,
              "ref_text": "Depois da chuva, a rua parecia um novo começo. O vento da tarde deixou a cidade um pouco mais calma.",
              "xvec_only": false,
              "non_streaming_mode": true
            },
            "model_revision": "fd4b254389122332181a7c3db7f27e918eec64e3",
            "reference_sha256": "47bd8f606bb8de073b916f39c69d97ca7b667a2fcf8fa3368d89690768ac1080",
            "encoding": {
              "codec": "opus",
              "container": "ogg",
              "bitrate": 64000,
              "vbr": true,
              "application": "audio",
              "compression_level": 10
            }
          },
          "fingerprint": "63654c4d8c4e29f9e4f7585d5e483d6db7ac1d6091461439c8852f191e74cb26",
          "sha256": "f2efe8adccaa798d148aa23e5f440cf2dd1521c861e71f0110f9ea596d6f8a60",
          "bytes": 31897,
          "duration_seconds": 3.926,
          "voice_profile": "clear_male",
          "reference": "references/portuguese/clear_male.flac"
        },
        {
          "file": "portuguese/random/07.opus",
          "text": "Na feira, os tomates pareciam mais organizados que minha semana.",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "mode": "clone",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
              "text": "Na feira, os tomates pareciam mais organizados que minha semana.",
              "language": "Portuguese",
              "seed": 8106,
              "ref_text": "Depois da chuva, a rua parecia um novo começo. O vento da tarde deixou a cidade um pouco mais calma.",
              "xvec_only": false,
              "non_streaming_mode": true
            },
            "model_revision": "fd4b254389122332181a7c3db7f27e918eec64e3",
            "reference_sha256": "059007cdbc116324fe604f5d4b05aee78df86584e1f4ea7a510fb6ab9728bd4b",
            "encoding": {
              "codec": "opus",
              "container": "ogg",
              "bitrate": 64000,
              "vbr": true,
              "application": "audio",
              "compression_level": 10
            }
          },
          "fingerprint": "07f3447c664ee29d2664e74e78041ab3d95a6769f7ff5f778f57e43c51df19ce",
          "sha256": "30ea49c3e47cc8cab4e470ee221295b011cc5c5a321f2c7676698f40e5c59089",
          "bytes": 33627,
          "duration_seconds": 4.247,
          "voice_profile": "relaxed_female",
          "reference": "references/portuguese/relaxed_female.flac"
        },
        {
          "file": "portuguese/random/08.opus",
          "text": "O trem atrasou, então todos estudaram o celular com seriedade.",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "mode": "clone",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
              "text": "O trem atrasou, então todos estudaram o celular com seriedade.",
              "language": "Portuguese",
              "seed": 8107,
              "ref_text": "Depois da chuva, a rua parecia um novo começo. O vento da tarde deixou a cidade um pouco mais calma.",
              "xvec_only": false,
              "non_streaming_mode": true
            },
            "model_revision": "fd4b254389122332181a7c3db7f27e918eec64e3",
            "reference_sha256": "b1b176510519f185ad11e0135a50ee3246e1c445da9b864e1dec53cec73fb49a",
            "encoding": {
              "codec": "opus",
              "container": "ogg",
              "bitrate": 64000,
              "vbr": true,
              "application": "audio",
              "compression_level": 10
            }
          },
          "fingerprint": "c905e60598bd19ce459e1c856db0a23f1b511c982f8f01acb4cf269025451cc2",
          "sha256": "a04f0e718e8d9fda32ddd11cc125ac226bb64e6d10a3cf6463de4f9e16368fc7",
          "bytes": 40164,
          "duration_seconds": 4.806,
          "voice_profile": "deep_male",
          "reference": "references/portuguese/deep_male.flac"
        },
        {
          "file": "portuguese/random/09.opus",
          "text": "Arrumei a mesa e encontrei uma caneta de um plano antigo.",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "mode": "clone",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
              "text": "Arrumei a mesa e encontrei uma caneta de um plano antigo.",
              "language": "Portuguese",
              "seed": 8108,
              "ref_text": "Depois da chuva, a rua parecia um novo começo. O vento da tarde deixou a cidade um pouco mais calma.",
              "xvec_only": false,
              "non_streaming_mode": true
            },
            "model_revision": "fd4b254389122332181a7c3db7f27e918eec64e3",
            "reference_sha256": "d05bc99bdf04c6424403d8007f8c86d013564f20009ef25cde4c688db7b28432",
            "encoding": {
              "codec": "opus",
              "container": "ogg",
              "bitrate": 64000,
              "vbr": true,
              "application": "audio",
              "compression_level": 10
            }
          },
          "fingerprint": "2c293713ce94f7c733b254e675ff4b80283daa6fb63b54d78cea09b55c38489c",
          "sha256": "c43ad1be94435c9984af2130a144290802e2781612d1711405fc20595fc0ec39",
          "bytes": 28931,
          "duration_seconds": 3.687,
          "voice_profile": "cheerful_female",
          "reference": "references/portuguese/cheerful_female.flac"
        },
        {
          "file": "portuguese/random/10.opus",
          "text": "O vento da tarde deixou a cidade um pouco mais calma.",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "mode": "clone",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
              "text": "O vento da tarde deixou a cidade um pouco mais calma.",
              "language": "Portuguese",
              "seed": 8109,
              "ref_text": "Depois da chuva, a rua parecia um novo começo. O vento da tarde deixou a cidade um pouco mais calma.",
              "xvec_only": false,
              "non_streaming_mode": true
            },
            "model_revision": "fd4b254389122332181a7c3db7f27e918eec64e3",
            "reference_sha256": "d9c06715615762b6478d3a0a48b1727ca97e8114f8465feaad412f8fd8426aee",
            "encoding": {
              "codec": "opus",
              "container": "ogg",
              "bitrate": 64000,
              "vbr": true,
              "application": "audio",
              "compression_level": 10
            }
          },
          "fingerprint": "ac9fe255fd24c9ebb78c05ac28923f3eff7700492d0e6cef402eab5c762314a7",
          "sha256": "9467a623d8c5d0f1ca3b337e26ff08b7714d7919eb5bd436f5e4b31f2d3e0291",
          "bytes": 28947,
          "duration_seconds": 3.526,
          "voice_profile": "balanced_male",
          "reference": "references/portuguese/balanced_male.flac"
        }
      ],
      "intro": [
        {
          "file": "portuguese/intro/01.opus",
          "text": "Olá, este é o Qwen Studio da Hangry Labs. Criamos ferramentas de voz locais e fáceis de executar para que as pessoas possam gerar fala com privacidade, offline e no próprio idioma.",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "mode": "clone",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
              "text": "Olá, este é o Qwen Studio da Hangry Labs. Criamos ferramentas de voz locais e fáceis de executar para que as pessoas possam gerar fala com privacidade, offline e no próprio idioma.",
              "language": "Portuguese",
              "seed": 8500,
              "ref_text": "Depois da chuva, a rua parecia um novo começo. O vento da tarde deixou a cidade um pouco mais calma.",
              "xvec_only": false,
              "non_streaming_mode": true
            },
            "model_revision": "fd4b254389122332181a7c3db7f27e918eec64e3",
            "reference_sha256": "76fa1c7387e61798edc751a02f74763dbd4498673e02458085a9c1f126d6c050",
            "encoding": {
              "codec": "opus",
              "container": "ogg",
              "bitrate": 64000,
              "vbr": true,
              "application": "audio",
              "compression_level": 10
            }
          },
          "fingerprint": "d5a9ea78184053fd0e230ecbbf43b4cc10fe14378266fc038f9d98d093eeee73",
          "sha256": "1f3af001b3afe16a5cb9401fe815375c3e53e930ca9a187b91cef8fafd3463e3",
          "bytes": 94592,
          "duration_seconds": 11.607,
          "voice_profile": "warm_female_narrator",
          "reference": "references/portuguese/warm_female_narrator.flac"
        },
        {
          "file": "portuguese/intro/02.opus",
          "text": "Olá, este é o Qwen Studio da Hangry Labs. Criamos ferramentas de voz locais e fáceis de executar para que as pessoas possam gerar fala com privacidade, offline e no próprio idioma.",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "mode": "clone",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
              "text": "Olá, este é o Qwen Studio da Hangry Labs. Criamos ferramentas de voz locais e fáceis de executar para que as pessoas possam gerar fala com privacidade, offline e no próprio idioma.",
              "language": "Portuguese",
              "seed": 8501,
              "ref_text": "Depois da chuva, a rua parecia um novo começo. O vento da tarde deixou a cidade um pouco mais calma.",
              "xvec_only": false,
              "non_streaming_mode": true
            },
            "model_revision": "fd4b254389122332181a7c3db7f27e918eec64e3",
            "reference_sha256": "e0b5cdf177a132ceb477c9e474ea70fa6626c39672bc27d20f5653f62110a1ba",
            "encoding": {
              "codec": "opus",
              "container": "ogg",
              "bitrate": 64000,
              "vbr": true,
              "application": "audio",
              "compression_level": 10
            }
          },
          "fingerprint": "370e485d8ce4d711d4e6a46a55ba66ed689140b255385af94bf91bc8101feff3",
          "sha256": "3c2363f6e68a6822d8dcd306c27fa11eea2323ddb371df1fa090cd99a4788b2d",
          "bytes": 92988,
          "duration_seconds": 10.966,
          "voice_profile": "confident_male",
          "reference": "references/portuguese/confident_male.flac"
        },
        {
          "file": "portuguese/intro/03.opus",
          "text": "Olá, este é o Qwen Studio da Hangry Labs. Criamos ferramentas de voz locais e fáceis de executar para que as pessoas possam gerar fala com privacidade, offline e no próprio idioma.",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "mode": "clone",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
              "text": "Olá, este é o Qwen Studio da Hangry Labs. Criamos ferramentas de voz locais e fáceis de executar para que as pessoas possam gerar fala com privacidade, offline e no próprio idioma.",
              "language": "Portuguese",
              "seed": 8502,
              "ref_text": "Depois da chuva, a rua parecia um novo começo. O vento da tarde deixou a cidade um pouco mais calma.",
              "xvec_only": false,
              "non_streaming_mode": true
            },
            "model_revision": "fd4b254389122332181a7c3db7f27e918eec64e3",
            "reference_sha256": "059007cdbc116324fe604f5d4b05aee78df86584e1f4ea7a510fb6ab9728bd4b",
            "encoding": {
              "codec": "opus",
              "container": "ogg",
              "bitrate": 64000,
              "vbr": true,
              "application": "audio",
              "compression_level": 10
            }
          },
          "fingerprint": "ea96cdedbc281381397c681378f03833e51bcd1f6406a9e7c1412a245ba6e879",
          "sha256": "4a0a42273c8036e8489c12687aeb0af36b566e8f62487a71ce63e81e24600cae",
          "bytes": 96166,
          "duration_seconds": 11.687,
          "voice_profile": "relaxed_female",
          "reference": "references/portuguese/relaxed_female.flac"
        }
      ],
      "clone": [
        {
          "file": "portuguese/clone/01.opus",
          "text": "Olá, este é o Qwen Studio da Hangry Labs. Criamos ferramentas de voz locais e fáceis de executar para que as pessoas possam gerar fala com privacidade, offline e no próprio idioma.",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "mode": "clone",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
              "text": "Olá, este é o Qwen Studio da Hangry Labs. Criamos ferramentas de voz locais e fáceis de executar para que as pessoas possam gerar fala com privacidade, offline e no próprio idioma.",
              "language": "Portuguese",
              "seed": 8600,
              "ref_text": "The little bookshop was quiet when I arrived. Outside, the rain had stopped, and warm sunlight was finding its way through the windows.",
              "xvec_only": false,
              "non_streaming_mode": true
            },
            "model_revision": "fd4b254389122332181a7c3db7f27e918eec64e3",
            "reference_sha256": "591dc509d7be0360448d36b7a16f4e5bc8587d6096af849ffb37a69a298d7075",
            "encoding": {
              "codec": "opus",
              "container": "ogg",
              "bitrate": 64000,
              "vbr": true,
              "application": "audio",
              "compression_level": 10
            }
          },
          "fingerprint": "163f4ebe38c9ae5e3145d6291860dce256dda8a81d5bf626634ce0d148d4b224",
          "sha256": "3b996cc8b20ab781504e31b81984589e14af5c68643c04e87ade8e9e1512cdd1",
          "bytes": 100151,
          "duration_seconds": 11.767,
          "voice_profile": "warm_female_narrator",
          "reference": "references/warm_female_narrator.flac"
        }
      ]
    },
    {
      "slug": "spanish",
      "language": "Spanish",
      "native_name": "Español",
      "icon": "ES",
      "intro_text": "Hola, esto es Qwen Studio de Hangry Labs. Creamos herramientas de voz locales y fáciles de ejecutar para que las personas puedan generar habla en privado, sin conexión y en su propio idioma.",
      "random": [
        {
          "file": "spanish/random/01.opus",
          "text": "El café de la mañana negoció duro, pero al final ayudó.",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "mode": "clone",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
              "text": "El café de la mañana negoció duro, pero al final ayudó.",
              "language": "Spanish",
              "seed": 8100,
              "ref_text": "Después de la lluvia, la calle parecía un nuevo comienzo. El viento de la tarde hizo que la ciudad sonara más tranquila.",
              "xvec_only": false,
              "non_streaming_mode": true
            },
            "model_revision": "fd4b254389122332181a7c3db7f27e918eec64e3",
            "reference_sha256": "6bcaeb53a66afce2196e4d80d21cad60b774c0a02c2c16be73a9de4278b67e86",
            "encoding": {
              "codec": "opus",
              "container": "ogg",
              "bitrate": 64000,
              "vbr": true,
              "application": "audio",
              "compression_level": 10
            }
          },
          "fingerprint": "d3a22d713859e8bd7240aeec6ca6c806d010d5fd1fc5d9411118754b1a2169f8",
          "sha256": "c55ec6a42d5a47c58f7a8f892f3cbc219e320b9750969a10ddbab4b5f5b9411b",
          "bytes": 30941,
          "duration_seconds": 3.607,
          "voice_profile": "warm_female_narrator",
          "reference": "references/spanish/warm_female_narrator.flac"
        },
        {
          "file": "spanish/random/02.opus",
          "text": "Guardé las llaves en un lugar seguro, quizá demasiado seguro.",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "mode": "clone",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
              "text": "Guardé las llaves en un lugar seguro, quizá demasiado seguro.",
              "language": "Spanish",
              "seed": 8101,
              "ref_text": "Después de la lluvia, la calle parecía un nuevo comienzo. El viento de la tarde hizo que la ciudad sonara más tranquila.",
              "xvec_only": false,
              "non_streaming_mode": true
            },
            "model_revision": "fd4b254389122332181a7c3db7f27e918eec64e3",
            "reference_sha256": "974855305359426667a36aaa0ebeb9cfcc812ebe0ac4bc164eafa30baaf57253",
            "encoding": {
              "codec": "opus",
              "container": "ogg",
              "bitrate": 64000,
              "vbr": true,
              "application": "audio",
              "compression_level": 10
            }
          },
          "fingerprint": "9ee4a1061fc3c76775a83d9e633c4a0b59e26063c7bc4108b4020b4ace14dbb2",
          "sha256": "778c8ae78ba8c39711bb6a552a42deb36f1a1110b09ab9630ff36ee45a1921bf",
          "bytes": 36489,
          "duration_seconds": 3.846,
          "voice_profile": "calm_male_narrator",
          "reference": "references/spanish/calm_male_narrator.flac"
        },
        {
          "file": "spanish/random/03.opus",
          "text": "Después de la lluvia, la calle parecía un nuevo comienzo.",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "mode": "clone",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
              "text": "Después de la lluvia, la calle parecía un nuevo comienzo.",
              "language": "Spanish",
              "seed": 8102,
              "ref_text": "Después de la lluvia, la calle parecía un nuevo comienzo. El viento de la tarde hizo que la ciudad sonara más tranquila.",
              "xvec_only": false,
              "non_streaming_mode": true
            },
            "model_revision": "fd4b254389122332181a7c3db7f27e918eec64e3",
            "reference_sha256": "7acf060eda868f1ecc12f920d445fab42a4ac0366b3e1501d82ff991b222a9bb",
            "encoding": {
              "codec": "opus",
              "container": "ogg",
              "bitrate": 64000,
              "vbr": true,
              "application": "audio",
              "compression_level": 10
            }
          },
          "fingerprint": "2b5658e721298149e83177c824cedd850bc697e656e65a4316154b99ceaa9dd2",
          "sha256": "cd2c5133c5494962b4986bf3aa4cd66526bce0c1747f5e02736fbc8ffe450171",
          "bytes": 39064,
          "duration_seconds": 4.646,
          "voice_profile": "bright_female",
          "reference": "references/spanish/bright_female.flac"
        },
        {
          "file": "spanish/random/04.opus",
          "text": "El olor de la panadería hizo que el desvío pareciera sensato.",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "mode": "clone",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
              "text": "El olor de la panadería hizo que el desvío pareciera sensato.",
              "language": "Spanish",
              "seed": 8103,
              "ref_text": "Después de la lluvia, la calle parecía un nuevo comienzo. El viento de la tarde hizo que la ciudad sonara más tranquila.",
              "xvec_only": false,
              "non_streaming_mode": true
            },
            "model_revision": "fd4b254389122332181a7c3db7f27e918eec64e3",
            "reference_sha256": "f3e01046bd4ce834bc2aee3c5a53cac7ef6d27efecbdb4413a965eb3bab5203b",
            "encoding": {
              "codec": "opus",
              "container": "ogg",
              "bitrate": 64000,
              "vbr": true,
              "application": "audio",
              "compression_level": 10
            }
          },
          "fingerprint": "6ecc7119c1a10835ba7ccb9bd27f6c51534ffbf7badb1b3bb1d101ebe19cb44d",
          "sha256": "0ca0ece3332fa401dc37d85d076c36b52736a8fcb3d821e3feeefe43485770a0",
          "bytes": 35559,
          "duration_seconds": 3.446,
          "voice_profile": "confident_male",
          "reference": "references/spanish/confident_male.flac"
        },
        {
          "file": "spanish/random/05.opus",
          "text": "Mi calendario tiene humor; el lunes vuelve justo después del domingo.",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "mode": "clone",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
              "text": "Mi calendario tiene humor; el lunes vuelve justo después del domingo.",
              "language": "Spanish",
              "seed": 8104,
              "ref_text": "Después de la lluvia, la calle parecía un nuevo comienzo. El viento de la tarde hizo que la ciudad sonara más tranquila.",
              "xvec_only": false,
              "non_streaming_mode": true
            },
            "model_revision": "fd4b254389122332181a7c3db7f27e918eec64e3",
            "reference_sha256": "89a2b3a75efce83d508c1b5906cb9f77a67953058df32a3b06e07c017d044d07",
            "encoding": {
              "codec": "opus",
              "container": "ogg",
              "bitrate": 64000,
              "vbr": true,
              "application": "audio",
              "compression_level": 10
            }
          },
          "fingerprint": "66753871e50f59764609d44c0593ac2af95f16961fbb1da921789a2df58da607",
          "sha256": "991a57c460433996f8f03e064b284a99a920229e1e289ef8e128715ceb444c12",
          "bytes": 47860,
          "duration_seconds": 5.686,
          "voice_profile": "gentle_female",
          "reference": "references/spanish/gentle_female.flac"
        },
        {
          "file": "spanish/random/06.opus",
          "text": "Quise escribir un mensaje corto y salió una pequeña historia.",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "mode": "clone",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
              "text": "Quise escribir un mensaje corto y salió una pequeña historia.",
              "language": "Spanish",
              "seed": 8105,
              "ref_text": "Después de la lluvia, la calle parecía un nuevo comienzo. El viento de la tarde hizo que la ciudad sonara más tranquila.",
              "xvec_only": false,
              "non_streaming_mode": true
            },
            "model_revision": "fd4b254389122332181a7c3db7f27e918eec64e3",
            "reference_sha256": "65f341028c31e27a2493c787bd722d3d9d1648bacd26604affe06734a9d90ec3",
            "encoding": {
              "codec": "opus",
              "container": "ogg",
              "bitrate": 64000,
              "vbr": true,
              "application": "audio",
              "compression_level": 10
            }
          },
          "fingerprint": "d765c3a9ca3ad57a8b71401de13e3611025b7628c9e21c3d61d6abe84a1fe3df",
          "sha256": "079b1da6573cfcd7d558c4bc673b733eb5035fb56abbf8240120ba605f601632",
          "bytes": 37619,
          "duration_seconds": 4.247,
          "voice_profile": "clear_male",
          "reference": "references/spanish/clear_male.flac"
        },
        {
          "file": "spanish/random/07.opus",
          "text": "En el mercado, los tomates parecían más organizados que mi semana.",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "mode": "clone",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
              "text": "En el mercado, los tomates parecían más organizados que mi semana.",
              "language": "Spanish",
              "seed": 8106,
              "ref_text": "Después de la lluvia, la calle parecía un nuevo comienzo. El viento de la tarde hizo que la ciudad sonara más tranquila.",
              "xvec_only": false,
              "non_streaming_mode": true
            },
            "model_revision": "fd4b254389122332181a7c3db7f27e918eec64e3",
            "reference_sha256": "7368a72a82dc7f06267e0bce59ed611853fa4bc6e865e2bae9886ac1a4c73f34",
            "encoding": {
              "codec": "opus",
              "container": "ogg",
              "bitrate": 64000,
              "vbr": true,
              "application": "audio",
              "compression_level": 10
            }
          },
          "fingerprint": "c60251571f3befa86941f3bace77f119b3912e17a37870569d0482e7a3b95d9c",
          "sha256": "b9295e27369017315e08e48d4e55d9d1beab676f08495d46fe40a6b3f7a6ce5c",
          "bytes": 37024,
          "duration_seconds": 4.407,
          "voice_profile": "relaxed_female",
          "reference": "references/spanish/relaxed_female.flac"
        },
        {
          "file": "spanish/random/08.opus",
          "text": "El tren llegó tarde, así que todos estudiaron el teléfono con seriedad.",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "mode": "clone",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
              "text": "El tren llegó tarde, así que todos estudiaron el teléfono con seriedad.",
              "language": "Spanish",
              "seed": 8107,
              "ref_text": "Después de la lluvia, la calle parecía un nuevo comienzo. El viento de la tarde hizo que la ciudad sonara más tranquila.",
              "xvec_only": false,
              "non_streaming_mode": true
            },
            "model_revision": "fd4b254389122332181a7c3db7f27e918eec64e3",
            "reference_sha256": "5a574a961b460b3e9795aa465f773e99d686cfc59d900370bbfa6893a6646fee",
            "encoding": {
              "codec": "opus",
              "container": "ogg",
              "bitrate": 64000,
              "vbr": true,
              "application": "audio",
              "compression_level": 10
            }
          },
          "fingerprint": "71c60fdea73c505023a80022574a21afa50bbb253bfd1d104c5055b7e1922660",
          "sha256": "b7a7c981a8d7234cba5c9b83542113b062fcb24e3b1e25eb93a7ac6aa10825c6",
          "bytes": 53539,
          "duration_seconds": 5.447,
          "voice_profile": "deep_male",
          "reference": "references/spanish/deep_male.flac"
        },
        {
          "file": "spanish/random/09.opus",
          "text": "Ordené el escritorio y encontré un bolígrafo de un plan antiguo.",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "mode": "clone",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
              "text": "Ordené el escritorio y encontré un bolígrafo de un plan antiguo.",
              "language": "Spanish",
              "seed": 8108,
              "ref_text": "Después de la lluvia, la calle parecía un nuevo comienzo. El viento de la tarde hizo que la ciudad sonara más tranquila.",
              "xvec_only": false,
              "non_streaming_mode": true
            },
            "model_revision": "fd4b254389122332181a7c3db7f27e918eec64e3",
            "reference_sha256": "cd1205ed7a2436d48634e1b128a4d3d7c4d13c5bea1018dcd86c6dad4111ac0e",
            "encoding": {
              "codec": "opus",
              "container": "ogg",
              "bitrate": 64000,
              "vbr": true,
              "application": "audio",
              "compression_level": 10
            }
          },
          "fingerprint": "cd461ff9a26a6a95292c4cfb1c6f5e04bcbc11243088eecaeaa621811b059085",
          "sha256": "d71a6ee4ce2a9a14df9f95c678d7f6a75ef7aee9a25347fc5f780cf56ac7f9fd",
          "bytes": 45655,
          "duration_seconds": 4.966,
          "voice_profile": "cheerful_female",
          "reference": "references/spanish/cheerful_female.flac"
        },
        {
          "file": "spanish/random/10.opus",
          "text": "El viento de la tarde hizo que la ciudad sonara más tranquila.",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "mode": "clone",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
              "text": "El viento de la tarde hizo que la ciudad sonara más tranquila.",
              "language": "Spanish",
              "seed": 8109,
              "ref_text": "Después de la lluvia, la calle parecía un nuevo comienzo. El viento de la tarde hizo que la ciudad sonara más tranquila.",
              "xvec_only": false,
              "non_streaming_mode": true
            },
            "model_revision": "fd4b254389122332181a7c3db7f27e918eec64e3",
            "reference_sha256": "e9c7af69002888e6083ed6ec0003342bafb6fb3e4a451b7ad689fa65a0e1eb5e",
            "encoding": {
              "codec": "opus",
              "container": "ogg",
              "bitrate": 64000,
              "vbr": true,
              "application": "audio",
              "compression_level": 10
            }
          },
          "fingerprint": "c94f66a5c4f129af9f9d5383321e0f8eadfac211a52e7eb85d4cc10ee0075db2",
          "sha256": "d5178b1cee1ce2ffd0a2f56df7ecb49041da8b8cb84272b25cb9666afec62142",
          "bytes": 38188,
          "duration_seconds": 4.087,
          "voice_profile": "balanced_male",
          "reference": "references/spanish/balanced_male.flac"
        }
      ],
      "intro": [
        {
          "file": "spanish/intro/01.opus",
          "text": "Hola, esto es Qwen Studio de Hangry Labs. Creamos herramientas de voz locales y fáciles de ejecutar para que las personas puedan generar habla en privado, sin conexión y en su propio idioma.",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "mode": "clone",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
              "text": "Hola, esto es Qwen Studio de Hangry Labs. Creamos herramientas de voz locales y fáciles de ejecutar para que las personas puedan generar habla en privado, sin conexión y en su propio idioma.",
              "language": "Spanish",
              "seed": 8500,
              "ref_text": "Después de la lluvia, la calle parecía un nuevo comienzo. El viento de la tarde hizo que la ciudad sonara más tranquila.",
              "xvec_only": false,
              "non_streaming_mode": true
            },
            "model_revision": "fd4b254389122332181a7c3db7f27e918eec64e3",
            "reference_sha256": "6bcaeb53a66afce2196e4d80d21cad60b774c0a02c2c16be73a9de4278b67e86",
            "encoding": {
              "codec": "opus",
              "container": "ogg",
              "bitrate": 64000,
              "vbr": true,
              "application": "audio",
              "compression_level": 10
            }
          },
          "fingerprint": "6d104a9bd290ca2c09902ffc18632c03e996abe089d2366f1ca563a01602df56",
          "sha256": "7daf7d12a49a562ea506f7da0490048cd66d1b443d78f41510e1d490ca55a10a",
          "bytes": 112481,
          "duration_seconds": 12.726,
          "voice_profile": "warm_female_narrator",
          "reference": "references/spanish/warm_female_narrator.flac"
        },
        {
          "file": "spanish/intro/02.opus",
          "text": "Hola, esto es Qwen Studio de Hangry Labs. Creamos herramientas de voz locales y fáciles de ejecutar para que las personas puedan generar habla en privado, sin conexión y en su propio idioma.",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "mode": "clone",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
              "text": "Hola, esto es Qwen Studio de Hangry Labs. Creamos herramientas de voz locales y fáciles de ejecutar para que las personas puedan generar habla en privado, sin conexión y en su propio idioma.",
              "language": "Spanish",
              "seed": 8501,
              "ref_text": "Después de la lluvia, la calle parecía un nuevo comienzo. El viento de la tarde hizo que la ciudad sonara más tranquila.",
              "xvec_only": false,
              "non_streaming_mode": true
            },
            "model_revision": "fd4b254389122332181a7c3db7f27e918eec64e3",
            "reference_sha256": "f3e01046bd4ce834bc2aee3c5a53cac7ef6d27efecbdb4413a965eb3bab5203b",
            "encoding": {
              "codec": "opus",
              "container": "ogg",
              "bitrate": 64000,
              "vbr": true,
              "application": "audio",
              "compression_level": 10
            }
          },
          "fingerprint": "8619a4244a82cbfc7d60215c819ecc01dbe61f218cdafd92897e32dfd7a54fdf",
          "sha256": "7e30906f244c85e1f95f9e9888cb7d46a2a8e03285b323ba9115fa78c7e5b1d7",
          "bytes": 111236,
          "duration_seconds": 11.046,
          "voice_profile": "confident_male",
          "reference": "references/spanish/confident_male.flac"
        },
        {
          "file": "spanish/intro/03.opus",
          "text": "Hola, esto es Qwen Studio de Hangry Labs. Creamos herramientas de voz locales y fáciles de ejecutar para que las personas puedan generar habla en privado, sin conexión y en su propio idioma.",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "mode": "clone",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
              "text": "Hola, esto es Qwen Studio de Hangry Labs. Creamos herramientas de voz locales y fáciles de ejecutar para que las personas puedan generar habla en privado, sin conexión y en su propio idioma.",
              "language": "Spanish",
              "seed": 8502,
              "ref_text": "Después de la lluvia, la calle parecía un nuevo comienzo. El viento de la tarde hizo que la ciudad sonara más tranquila.",
              "xvec_only": false,
              "non_streaming_mode": true
            },
            "model_revision": "fd4b254389122332181a7c3db7f27e918eec64e3",
            "reference_sha256": "7368a72a82dc7f06267e0bce59ed611853fa4bc6e865e2bae9886ac1a4c73f34",
            "encoding": {
              "codec": "opus",
              "container": "ogg",
              "bitrate": 64000,
              "vbr": true,
              "application": "audio",
              "compression_level": 10
            }
          },
          "fingerprint": "25231881a5fdbe4235f6c1f3e08750b7a6ba0a6d3b6d4024aa532fe2a6308773",
          "sha256": "d12b9cfe442bfe7f0aeb13cfe57e315c3b320deb02e6757488d4a3205e15b7ed",
          "bytes": 104239,
          "duration_seconds": 12.007,
          "voice_profile": "relaxed_female",
          "reference": "references/spanish/relaxed_female.flac"
        }
      ],
      "clone": [
        {
          "file": "spanish/clone/01.opus",
          "text": "Hola, esto es Qwen Studio de Hangry Labs. Creamos herramientas de voz locales y fáciles de ejecutar para que las personas puedan generar habla en privado, sin conexión y en su propio idioma.",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "mode": "clone",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
              "text": "Hola, esto es Qwen Studio de Hangry Labs. Creamos herramientas de voz locales y fáciles de ejecutar para que las personas puedan generar habla en privado, sin conexión y en su propio idioma.",
              "language": "Spanish",
              "seed": 8600,
              "ref_text": "The little bookshop was quiet when I arrived. Outside, the rain had stopped, and warm sunlight was finding its way through the windows.",
              "xvec_only": false,
              "non_streaming_mode": true
            },
            "model_revision": "fd4b254389122332181a7c3db7f27e918eec64e3",
            "reference_sha256": "591dc509d7be0360448d36b7a16f4e5bc8587d6096af849ffb37a69a298d7075",
            "encoding": {
              "codec": "opus",
              "container": "ogg",
              "bitrate": 64000,
              "vbr": true,
              "application": "audio",
              "compression_level": 10
            }
          },
          "fingerprint": "9e8e1a3a976530048e7975ddcf37e3ddd54597c5e59cce89a3b26b6530dd705e",
          "sha256": "2f9072584a7298cfb6462f0ea58fe55cc5cd433731502b54cb9b2d5fe5866774",
          "bytes": 118140,
          "duration_seconds": 13.527,
          "voice_profile": "warm_female_narrator",
          "reference": "references/warm_female_narrator.flac"
        }
      ]
    },
    {
      "slug": "italian",
      "language": "Italian",
      "native_name": "Italiano",
      "icon": "IT",
      "intro_text": "Ciao, questo è Qwen Studio di Hangry Labs. Costruiamo strumenti vocali locali e facili da avviare, così le persone possono creare parlato in privato, offline e nella propria lingua.",
      "random": [
        {
          "file": "italian/random/01.opus",
          "text": "Il caffè del mattino ha trattato duramente, ma poi ha aiutato.",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "mode": "clone",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
              "text": "Il caffè del mattino ha trattato duramente, ma poi ha aiutato.",
              "language": "Italian",
              "seed": 8100,
              "ref_text": "Dopo la pioggia, la strada sembrava un nuovo inizio. Il vento della sera ha reso la città più calma.",
              "xvec_only": false,
              "non_streaming_mode": true
            },
            "model_revision": "fd4b254389122332181a7c3db7f27e918eec64e3",
            "reference_sha256": "06d71f977084e685527eae941a29ac1416ecc553c7a9b8ce1168f1c46b2ba266",
            "encoding": {
              "codec": "opus",
              "container": "ogg",
              "bitrate": 64000,
              "vbr": true,
              "application": "audio",
              "compression_level": 10
            }
          },
          "fingerprint": "bfecb41e189314e606bf1346b4f3cf67a728676fecdbfe815b8345ce249a413b",
          "sha256": "ce92256742172d4487309dfbd38f903d99f040ac054e5005bad51062b44f28ac",
          "bytes": 44876,
          "duration_seconds": 4.887,
          "voice_profile": "warm_female_narrator",
          "reference": "references/italian/warm_female_narrator.flac"
        },
        {
          "file": "italian/random/02.opus",
          "text": "Ho messo le chiavi in un posto sicuro, forse troppo sicuro.",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "mode": "clone",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
              "text": "Ho messo le chiavi in un posto sicuro, forse troppo sicuro.",
              "language": "Italian",
              "seed": 8101,
              "ref_text": "Dopo la pioggia, la strada sembrava un nuovo inizio. Il vento della sera ha reso la città più calma.",
              "xvec_only": false,
              "non_streaming_mode": true
            },
            "model_revision": "fd4b254389122332181a7c3db7f27e918eec64e3",
            "reference_sha256": "697133a044e702be36589cd32f0339207cff4f4a27d1ebfe78fbd7306588230c",
            "encoding": {
              "codec": "opus",
              "container": "ogg",
              "bitrate": 64000,
              "vbr": true,
              "application": "audio",
              "compression_level": 10
            }
          },
          "fingerprint": "7e7e96a994b99f5b154a68c03faea8abe403756da856abec4b641040486104a6",
          "sha256": "a7dc1dff888d8320115108a70c79d8647ad4e3659315ef1cb86b8307cd694d81",
          "bytes": 35958,
          "duration_seconds": 3.846,
          "voice_profile": "calm_male_narrator",
          "reference": "references/italian/calm_male_narrator.flac"
        },
        {
          "file": "italian/random/03.opus",
          "text": "Dopo la pioggia, la strada sembrava un nuovo inizio.",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "mode": "clone",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
              "text": "Dopo la pioggia, la strada sembrava un nuovo inizio.",
              "language": "Italian",
              "seed": 8102,
              "ref_text": "Dopo la pioggia, la strada sembrava un nuovo inizio. Il vento della sera ha reso la città più calma.",
              "xvec_only": false,
              "non_streaming_mode": true
            },
            "model_revision": "fd4b254389122332181a7c3db7f27e918eec64e3",
            "reference_sha256": "1d9b50f5e09110d7557b96376c9fe1223f6ea74f7a5e0b5f155b7cca39f6bea6",
            "encoding": {
              "codec": "opus",
              "container": "ogg",
              "bitrate": 64000,
              "vbr": true,
              "application": "audio",
              "compression_level": 10
            }
          },
          "fingerprint": "9c67325b9809c1d95468e5baf3e759daa0dafbf4934d9985811ba85b988e6358",
          "sha256": "f588c2851390838eb7b43169f3c78315d62483ed6f9e7d47d3bb6ed9c0c441ff",
          "bytes": 27731,
          "duration_seconds": 2.966,
          "voice_profile": "bright_female",
          "reference": "references/italian/bright_female.flac"
        },
        {
          "file": "italian/random/04.opus",
          "text": "Il profumo del forno ha reso la deviazione molto sensata.",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "mode": "clone",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
              "text": "Il profumo del forno ha reso la deviazione molto sensata.",
              "language": "Italian",
              "seed": 8103,
              "ref_text": "Dopo la pioggia, la strada sembrava un nuovo inizio. Il vento della sera ha reso la città più calma.",
              "xvec_only": false,
              "non_streaming_mode": true
            },
            "model_revision": "fd4b254389122332181a7c3db7f27e918eec64e3",
            "reference_sha256": "ba1d9120594f46f3295f5bf1a9327dbdc79fd5b79065e36922be75b5605dd12b",
            "encoding": {
              "codec": "opus",
              "container": "ogg",
              "bitrate": 64000,
              "vbr": true,
              "application": "audio",
              "compression_level": 10
            }
          },
          "fingerprint": "6bfef2b4f914a038471c735b207a5a2cc494ba8bf2f3645fbb3bea317edbdd63",
          "sha256": "96ce6bccb5e5b6ed768c1b03e135bd07d8f5447851e0537b1dfeb14b4ec4a2b5",
          "bytes": 30789,
          "duration_seconds": 3.127,
          "voice_profile": "confident_male",
          "reference": "references/italian/confident_male.flac"
        },
        {
          "file": "italian/random/05.opus",
          "text": "Il mio calendario scherza; lunedì arriva ancora dopo domenica.",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "mode": "clone",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
              "text": "Il mio calendario scherza; lunedì arriva ancora dopo domenica.",
              "language": "Italian",
              "seed": 8104,
              "ref_text": "Dopo la pioggia, la strada sembrava un nuovo inizio. Il vento della sera ha reso la città più calma.",
              "xvec_only": false,
              "non_streaming_mode": true
            },
            "model_revision": "fd4b254389122332181a7c3db7f27e918eec64e3",
            "reference_sha256": "e6e8c20d0c5c1a94ad6aab78b495766c44db462c60481cb4d6e85c8d3c893b6a",
            "encoding": {
              "codec": "opus",
              "container": "ogg",
              "bitrate": 64000,
              "vbr": true,
              "application": "audio",
              "compression_level": 10
            }
          },
          "fingerprint": "b94359770c114a6e25b6fb1a38b5e1ee467b4faf80f551db358cfb1a41b2095a",
          "sha256": "71ddd845cd201f93f22405d52411e434e31758185cedc7348ec26778a2dedba8",
          "bytes": 38995,
          "duration_seconds": 4.407,
          "voice_profile": "gentle_female",
          "reference": "references/italian/gentle_female.flac"
        },
        {
          "file": "italian/random/06.opus",
          "text": "Volevo scrivere un messaggio breve ed è uscito un piccolo romanzo.",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "mode": "clone",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
              "text": "Volevo scrivere un messaggio breve ed è uscito un piccolo romanzo.",
              "language": "Italian",
              "seed": 8105,
              "ref_text": "Dopo la pioggia, la strada sembrava un nuovo inizio. Il vento della sera ha reso la città più calma.",
              "xvec_only": false,
              "non_streaming_mode": true
            },
            "model_revision": "fd4b254389122332181a7c3db7f27e918eec64e3",
            "reference_sha256": "00e14348771f0fa77ffa8f3ff2ec782cbf362466e4de2ea4f8c4f8a3cde622a0",
            "encoding": {
              "codec": "opus",
              "container": "ogg",
              "bitrate": 64000,
              "vbr": true,
              "application": "audio",
              "compression_level": 10
            }
          },
          "fingerprint": "27fb175dfbca6bff17783b2199e3f6dd0da42f500966c522f69b7119960627bc",
          "sha256": "2e265a7e28800438ba0929ef9c8fb804b8e6ef77c9d705871b47288f8b6e8018",
          "bytes": 33020,
          "duration_seconds": 3.526,
          "voice_profile": "clear_male",
          "reference": "references/italian/clear_male.flac"
        },
        {
          "file": "italian/random/07.opus",
          "text": "Al mercato, i pomodori sembravano più organizzati della mia settimana.",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "mode": "clone",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
              "text": "Al mercato, i pomodori sembravano più organizzati della mia settimana.",
              "language": "Italian",
              "seed": 8106,
              "ref_text": "Dopo la pioggia, la strada sembrava un nuovo inizio. Il vento della sera ha reso la città più calma.",
              "xvec_only": false,
              "non_streaming_mode": true
            },
            "model_revision": "fd4b254389122332181a7c3db7f27e918eec64e3",
            "reference_sha256": "4d3d2a8ce56b3c3080e209d5503c63b7e1bb20fe4072f1ecb4d7a6f2139983bd",
            "encoding": {
              "codec": "opus",
              "container": "ogg",
              "bitrate": 64000,
              "vbr": true,
              "application": "audio",
              "compression_level": 10
            }
          },
          "fingerprint": "faac3cb8d6be9de55d1da17d631e427996642b99d44afdcaa22626a4cf630766",
          "sha256": "971af6a282915d5c6e34c5e1e3234a1b98c9a094d0a79df1a236118091dff130",
          "bytes": 40496,
          "duration_seconds": 4.566,
          "voice_profile": "relaxed_female",
          "reference": "references/italian/relaxed_female.flac"
        },
        {
          "file": "italian/random/08.opus",
          "text": "Il treno era in ritardo, quindi tutti hanno studiato il telefono con serietà.",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "mode": "clone",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
              "text": "Il treno era in ritardo, quindi tutti hanno studiato il telefono con serietà.",
              "language": "Italian",
              "seed": 8107,
              "ref_text": "Dopo la pioggia, la strada sembrava un nuovo inizio. Il vento della sera ha reso la città più calma.",
              "xvec_only": false,
              "non_streaming_mode": true
            },
            "model_revision": "fd4b254389122332181a7c3db7f27e918eec64e3",
            "reference_sha256": "fbfc0c6d4540f0e1015204a42257ca2ee9c19a36ebe5341cfb9581e15e34f99b",
            "encoding": {
              "codec": "opus",
              "container": "ogg",
              "bitrate": 64000,
              "vbr": true,
              "application": "audio",
              "compression_level": 10
            }
          },
          "fingerprint": "e97d7f5cb750e741359bd9db5b8fcf451fd223b1c7cd133f19c061f27d5b115e",
          "sha256": "f18b8d6d9a4e0b2994cf111f95ab51af46e6dc78b94546c851a3b4a039a468e1",
          "bytes": 46462,
          "duration_seconds": 4.726,
          "voice_profile": "deep_male",
          "reference": "references/italian/deep_male.flac"
        },
        {
          "file": "italian/random/09.opus",
          "text": "Ho riordinato la scrivania e trovato una penna di un vecchio piano.",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "mode": "clone",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
              "text": "Ho riordinato la scrivania e trovato una penna di un vecchio piano.",
              "language": "Italian",
              "seed": 8108,
              "ref_text": "Dopo la pioggia, la strada sembrava un nuovo inizio. Il vento della sera ha reso la città più calma.",
              "xvec_only": false,
              "non_streaming_mode": true
            },
            "model_revision": "fd4b254389122332181a7c3db7f27e918eec64e3",
            "reference_sha256": "c445f88bc7b3e0f4b01a0e169890d18e408b502559437c41bd351f7c6eee8013",
            "encoding": {
              "codec": "opus",
              "container": "ogg",
              "bitrate": 64000,
              "vbr": true,
              "application": "audio",
              "compression_level": 10
            }
          },
          "fingerprint": "4c48a1270b64af62f2dcbd71c0f7528c138af12c0d3f2bea5602274227368632",
          "sha256": "a414d38c87eb81d67649b6ada287609a8277bb9e183ac76439f3fb1894a07b4c",
          "bytes": 31984,
          "duration_seconds": 3.287,
          "voice_profile": "cheerful_female",
          "reference": "references/italian/cheerful_female.flac"
        },
        {
          "file": "italian/random/10.opus",
          "text": "Il vento della sera ha reso la città più calma.",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "mode": "clone",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
              "text": "Il vento della sera ha reso la città più calma.",
              "language": "Italian",
              "seed": 8109,
              "ref_text": "Dopo la pioggia, la strada sembrava un nuovo inizio. Il vento della sera ha reso la città più calma.",
              "xvec_only": false,
              "non_streaming_mode": true
            },
            "model_revision": "fd4b254389122332181a7c3db7f27e918eec64e3",
            "reference_sha256": "6c862c221920e6dcc477b37c8eb9e349c51ffb2e835e3e4d482d19ba8b261617",
            "encoding": {
              "codec": "opus",
              "container": "ogg",
              "bitrate": 64000,
              "vbr": true,
              "application": "audio",
              "compression_level": 10
            }
          },
          "fingerprint": "5335266912634c947ca6b8b18ec1ced758a54dfcb984a7f03c00e9a4fbe9ef8b",
          "sha256": "8494cbcc08ca75db90d9004ee53d3086201478464fc0e2144438553e6781b761",
          "bytes": 25160,
          "duration_seconds": 2.647,
          "voice_profile": "balanced_male",
          "reference": "references/italian/balanced_male.flac"
        }
      ],
      "intro": [
        {
          "file": "italian/intro/01.opus",
          "text": "Ciao, questo è Qwen Studio di Hangry Labs. Costruiamo strumenti vocali locali e facili da avviare, così le persone possono creare parlato in privato, offline e nella propria lingua.",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "mode": "clone",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
              "text": "Ciao, questo è Qwen Studio di Hangry Labs. Costruiamo strumenti vocali locali e facili da avviare, così le persone possono creare parlato in privato, offline e nella propria lingua.",
              "language": "Italian",
              "seed": 8500,
              "ref_text": "Dopo la pioggia, la strada sembrava un nuovo inizio. Il vento della sera ha reso la città più calma.",
              "xvec_only": false,
              "non_streaming_mode": true
            },
            "model_revision": "fd4b254389122332181a7c3db7f27e918eec64e3",
            "reference_sha256": "06d71f977084e685527eae941a29ac1416ecc553c7a9b8ce1168f1c46b2ba266",
            "encoding": {
              "codec": "opus",
              "container": "ogg",
              "bitrate": 64000,
              "vbr": true,
              "application": "audio",
              "compression_level": 10
            }
          },
          "fingerprint": "3f2d459082a1f6d694960ce5b314cc794c6da3dad6f2b196233131f234ca1184",
          "sha256": "84c607ee0af5720f80f3d67d35bf1912da750b27e0e5cdbcb12b58bff94f77dc",
          "bytes": 106753,
          "duration_seconds": 11.847,
          "voice_profile": "warm_female_narrator",
          "reference": "references/italian/warm_female_narrator.flac"
        },
        {
          "file": "italian/intro/02.opus",
          "text": "Ciao, questo è Qwen Studio di Hangry Labs. Costruiamo strumenti vocali locali e facili da avviare, così le persone possono creare parlato in privato, offline e nella propria lingua.",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "mode": "clone",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
              "text": "Ciao, questo è Qwen Studio di Hangry Labs. Costruiamo strumenti vocali locali e facili da avviare, così le persone possono creare parlato in privato, offline e nella propria lingua.",
              "language": "Italian",
              "seed": 8501,
              "ref_text": "Dopo la pioggia, la strada sembrava un nuovo inizio. Il vento della sera ha reso la città più calma.",
              "xvec_only": false,
              "non_streaming_mode": true
            },
            "model_revision": "fd4b254389122332181a7c3db7f27e918eec64e3",
            "reference_sha256": "ba1d9120594f46f3295f5bf1a9327dbdc79fd5b79065e36922be75b5605dd12b",
            "encoding": {
              "codec": "opus",
              "container": "ogg",
              "bitrate": 64000,
              "vbr": true,
              "application": "audio",
              "compression_level": 10
            }
          },
          "fingerprint": "241e4d2d7feb8422bec44a13169bd73a3564fb16d3ffad5a681f84fdf9062edf",
          "sha256": "055e18646c1ce2c4e900c889d93e43262f3d2f13bfde21f8d5edbdc4771b700a",
          "bytes": 99324,
          "duration_seconds": 10.966,
          "voice_profile": "confident_male",
          "reference": "references/italian/confident_male.flac"
        },
        {
          "file": "italian/intro/03.opus",
          "text": "Ciao, questo è Qwen Studio di Hangry Labs. Costruiamo strumenti vocali locali e facili da avviare, così le persone possono creare parlato in privato, offline e nella propria lingua.",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "mode": "clone",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
              "text": "Ciao, questo è Qwen Studio di Hangry Labs. Costruiamo strumenti vocali locali e facili da avviare, così le persone possono creare parlato in privato, offline e nella propria lingua.",
              "language": "Italian",
              "seed": 8502,
              "ref_text": "Dopo la pioggia, la strada sembrava un nuovo inizio. Il vento della sera ha reso la città più calma.",
              "xvec_only": false,
              "non_streaming_mode": true
            },
            "model_revision": "fd4b254389122332181a7c3db7f27e918eec64e3",
            "reference_sha256": "4d3d2a8ce56b3c3080e209d5503c63b7e1bb20fe4072f1ecb4d7a6f2139983bd",
            "encoding": {
              "codec": "opus",
              "container": "ogg",
              "bitrate": 64000,
              "vbr": true,
              "application": "audio",
              "compression_level": 10
            }
          },
          "fingerprint": "82292cff24e1433e4e4bd00610c7617a787bdcdd377764acdd9236919df1cee6",
          "sha256": "f8e07f0f1459d0c86a1bbb2c9140583efad59ab08ca1a21e939e46cde40c8f6b",
          "bytes": 110396,
          "duration_seconds": 12.486,
          "voice_profile": "relaxed_female",
          "reference": "references/italian/relaxed_female.flac"
        }
      ],
      "clone": [
        {
          "file": "italian/clone/01.opus",
          "text": "Ciao, questo è Qwen Studio di Hangry Labs. Costruiamo strumenti vocali locali e facili da avviare, così le persone possono creare parlato in privato, offline e nella propria lingua.",
          "recipe": {
            "request": {
              "temperature": 0.9,
              "top_k": 50,
              "repetition_penalty": 1.05,
              "max_new_tokens": 600,
              "chunk_size": 8,
              "decoder_context_frames": 25,
              "mode": "clone",
              "model": "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
              "text": "Ciao, questo è Qwen Studio di Hangry Labs. Costruiamo strumenti vocali locali e facili da avviare, così le persone possono creare parlato in privato, offline e nella propria lingua.",
              "language": "Italian",
              "seed": 8600,
              "ref_text": "The little bookshop was quiet when I arrived. Outside, the rain had stopped, and warm sunlight was finding its way through the windows.",
              "xvec_only": false,
              "non_streaming_mode": true
            },
            "model_revision": "fd4b254389122332181a7c3db7f27e918eec64e3",
            "reference_sha256": "591dc509d7be0360448d36b7a16f4e5bc8587d6096af849ffb37a69a298d7075",
            "encoding": {
              "codec": "opus",
              "container": "ogg",
              "bitrate": 64000,
              "vbr": true,
              "application": "audio",
              "compression_level": 10
            }
          },
          "fingerprint": "db4e1af4b8d7c9f80f0d27144ed7be9f531735b69ae7d72e75c4c92123ee76aa",
          "sha256": "d7efde89b00476f28a3ff31c3800d2e97b7bc97ac822bd16f3775006e909d68f",
          "bytes": 112618,
          "duration_seconds": 12.646,
          "voice_profile": "warm_female_narrator",
          "reference": "references/warm_female_narrator.flac"
        }
      ]
    }
  ],
  "featured_examples": [
    {
      "file": "featured/three-designed-voices.opus",
      "recipe": {
        "request": {
          "temperature": 0.9,
          "top_k": 50,
          "repetition_penalty": 1.05,
          "max_new_tokens": 600,
          "chunk_size": 8,
          "decoder_context_frames": 25,
          "input_type": "ssml-h",
          "text": "<speak version=\"1.1\" xmlns=\"http://www.w3.org/2001/10/synthesis\"\n       xmlns:h=\"https://hangrylabs.app/ns/ssml-h/1.0\" xml:lang=\"en-US\">\n  <metadata><h:extensions version=\"1.0\">\n    <h:voice-definition name=\"Lena\" scope=\"request\" seed=\"7300\">\n      <h:description>A warm adult woman with a rich middle register, gentle breath, clear diction and an inviting storytelling rhythm.</h:description>\n      <h:sample xml:lang=\"en-US\">The little bookshop was quiet when I arrived. Outside, the rain had stopped, and warm sunlight was finding its way through the windows.</h:sample>\n    </h:voice-definition>\n    <h:voice-definition name=\"Orion\" scope=\"request\" seed=\"7301\">\n      <h:description>A calm adult man with a resonant baritone, unhurried phrasing and a reassuring, softly textured voice.</h:description>\n      <h:sample xml:lang=\"en-US\">The little bookshop was quiet when I arrived. Outside, the rain had stopped, and warm sunlight was finding its way through the windows.</h:sample>\n    </h:voice-definition>\n    <h:voice-definition name=\"Pip\" scope=\"request\" seed=\"7308\">\n      <h:description>A cheerful adult woman with a buoyant middle-high voice, playful intonation and upbeat but natural energy.</h:description>\n      <h:sample xml:lang=\"en-US\">The little bookshop was quiet when I arrived. Outside, the rain had stopped, and warm sunlight was finding its way through the windows.</h:sample>\n    </h:voice-definition>\n  </h:extensions></metadata>\n  <voice name=\"Lena\">The voice lab is ready. Have we checked the microphone?</voice>\n  <break time=\"300ms\"/>\n  <voice name=\"Orion\">Twice. Even the kettle has promised to stay quiet.</voice>\n  <break time=\"300ms\"/>\n  <voice name=\"Pip\">Perfect. Three different voices, and one very important cup of tea.</voice>\n</speak>\n",
          "model": "auto",
          "language": "English",
          "seed": 9100,
          "non_streaming_mode": true,
          "output_format": "wav"
        },
        "models": {
          "design": {
            "id": "Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign",
            "revision": "5ecdb67327fd37bb2e042aab12ff7391903235d3"
          },
          "clone": {
            "id": "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
            "revision": "fd4b254389122332181a7c3db7f27e918eec64e3"
          }
        },
        "encoding": {
          "codec": "opus",
          "container": "ogg",
          "bitrate": 64000,
          "vbr": true,
          "application": "audio",
          "compression_level": 10
        }
      },
      "fingerprint": "324aa26b4447cf4b8f6e85bc7c393fbff834e4f765ed8bda8e1f6213cdc3ac50",
      "sha256": "620a7e027236baffce75d9e1043ffef040435bc1cdcd1890456f8b26d4c1cdb0",
      "bytes": 104141,
      "duration_seconds": 11.932,
      "eyebrow": "Designed characters",
      "title": "Three voices in the voice lab",
      "description": "A three-character SSML-H scene. Each voice is designed from its description, then reused for its dialogue. Two explicit pauses keep the turns clear.",
      "label": "Three designed voices dialogue",
      "badge": "SSML-H",
      "document": "ssml-h/three-designed-voices.ssml"
    }
  ]
};
