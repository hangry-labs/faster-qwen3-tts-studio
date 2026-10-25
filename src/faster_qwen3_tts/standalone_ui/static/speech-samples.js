// Speech content follows the synthesis language, independently of UI locale.
const SAMPLES = {
  English: 'Good morning! It is a lovely day to give your ideas a voice.',
  Chinese: '早上好！今天真适合让你的创意发声。放松下来，一起听听这个故事吧。',
  Japanese: 'おはようございます！今日はあなたのアイデアに声を与える素敵な日です。ゆっくり物語を楽しみましょう。',
  Korean: '좋은 아침이에요! 오늘은 여러분의 아이디어에 목소리를 더하기 좋은 날이에요. 편안하게 이야기를 들어 보세요.',
  German: 'Guten Morgen! Heute ist ein wunderbarer Tag, um deinen Ideen eine Stimme zu geben. Mach es dir gemütlich und höre der Geschichte zu.',
  French: 'Bonjour ! Quelle belle journée pour donner une voix à vos idées. Installez-vous et laissez le récit commencer.',
  Russian: 'Доброе утро! Сегодня прекрасный день, чтобы дать вашим идеям голос. Устройтесь поудобнее и послушайте эту историю.',
  Portuguese: 'Bom dia! Hoje é um ótimo dia para dar voz às suas ideias. Acomode-se e deixe a história começar.',
  Spanish: '¡Buenos días! Hoy es un día estupendo para dar voz a tus ideas. Ponte cómodo y deja que comience la historia.',
  Italian: 'Buongiorno! È una splendida giornata per dare voce alle tue idee. Mettiti comodo e lascia che la storia abbia inizio.',
}

export function speechSample(language, mode = 'custom') {
  if (language === 'English' && mode === 'design') return 'Welcome to our little corner of the world. Take a breath, settle in, and let the story begin.'
  if (language === 'English' && mode === 'clone') return 'This is a new sentence, spoken with the voice from my reference recording.'
  return SAMPLES[language] || SAMPLES.English
}
