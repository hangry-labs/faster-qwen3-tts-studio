// Qwen adapter for the shared VoxCPMTTS dialogue editor and workspace contracts.
import { MagicEditor } from './magic-editor.js'
import { MagicTakeStudio } from './magic-takes.js'
import { DialogueScriptLibrary } from './dialogue-script-library.js'
import { renderedSpeechText, serializeMagicDocument } from './magic-document.js'
import { encodeWav } from './audio-utils.js'
import { InputDrafts } from './input-drafts.js'
import { GenerationToolbar } from './generation-toolbar.js'
import { AudioFinisher } from './audio-finisher.js'
import { AudioEditor } from './audio-editor.js'
import { StreamWaveform, IncrementalAudioPlayback } from './streaming-player.js'
import { closeDialogOnBackdrop } from './dialog-utils.js'
import { generateRequestId } from './request-id.js'

const $ = selector => document.querySelector(selector)

export class GenerateWorkbench {
  constructor({ options, fetchJson, toast, onOutput, onBusy, onMetrics, outputEditor, restoreSettings, saveVoice }) {
    Object.assign(this, { options, fetchJson, toast, onOutput, onBusy, onMetrics, outputEditor, restoreSettings })
    this.inputType = 'magic'
    this.controller = null
    this.library = null
    this.output = null
    this.takes = new MagicTakeStudio({ responseError: async response => {
      const data = await response.json()
      return typeof data.detail === 'string' ? data.detail : JSON.stringify(data)
    } })
    this.editor = new MagicEditor($('#magic-editor-shell'), {
      onChange: () => { this.count(); this.library?.markDirty(); this.scheduleAssembly() },
      onPreview: block => this.job(async signal => {
        const index = this.editor.speechBlocks().findIndex(item => item.id === block.id)
        const requestId = generateRequestId(), monitor = new AbortController()
        const stop = () => monitor.abort()
        signal.addEventListener('abort', stop, { once: true })
        const watching = this.watchProgress(requestId, monitor.signal)
        try {
          const result = await this.takes.take(this.payload(), index, { signal, requestId })
          this.latestTakeGenerationTime = performance.now()
          monitor.abort(); await watching
          $('#last-generated-seed').value = result.seed; this.toolbar.sync()
          this.progress('complete', 'Turn ready', 'The completed dialogue will be assembled automatically')
          return result
        } finally { monitor.abort(); await watching; signal.removeEventListener('abort', stop) }
      }),
      onSaveCharacter: async block => {
        const preview = await this.editor.ensurePreview(block.id)
        saveVoice(new File([preview.blob], 'character.wav', { type: 'audio/wav' }), renderedSpeechText(block),
          { metrics: { seed: preview.seed }, recipe: { workflow: 'custom', settings: {
            ...this.payload(), text: this.editor.toSSMLH([block], { preview: true }), ui_input_type: 'magic',
          } }, finishing: { options: {} } })
      },
      onPersistCharacter: async ({ definition, block, metadata }) => {
        if (!block.preview?.blob) throw new Error('Generate a character turn before saving its voice.')
        const form = new FormData()
        form.set('name', definition.name); form.set('ref_text', renderedSpeechText(block))
        form.set('reference_audio', block.preview.blob, 'voice.wav')
        form.set('description', definition.description || '')
        form.set('replace', String(!!definition.replace))
        form.set('language', block.language || this.payload().language || 'English')
        form.set('tags', JSON.stringify(metadata?.tags || []))
        if (metadata?.portrait) form.set('portrait', metadata.portrait)
        form.set('recipe', JSON.stringify({ version: 1, workflow: 'custom', character: definition,
          settings: { ...this.payload(), text: this.editor.toSSMLH([block], { preview: true }),
            seed: block.preview.seed, randomize_seed: false, ui_input_type: 'magic' },
          selected_version: 'original' }))
        if (definition.replace && !confirm(`Replace the saved voice “${definition.name}” with this generated character recording?`)) {
          throw new Error('Voice replacement cancelled.')
        }
        const profile = await fetchJson('/tts/voice-profiles', { method: 'POST', body: form })
        await this.refreshVoices(); window.dispatchEvent(new Event('voice-library-changed'))
        return { profileId: profile.id }
      },
      onError: error => toast(error.message || error),
      onHistoryChange: history => {
        $('#dialogue-undo').disabled = !history.canUndo
        $('#dialogue-redo').disabled = !history.canRedo
      },
    })
    this.library = new DialogueScriptLibrary({ magicEditor: this.editor, fetchJson, showToast: toast,
      errorMessage: error => error.message || String(error), getInputType: () => this.inputType,
      setInputType: (type, options) => this.setInputType(type, options), onDocumentChange: () => this.count(),
      captureWorkspace: () => this.captureWorkspace(),
      restoreWorkspace: workspace => this.restoreWorkspace(workspace),
      clearWorkspace: () => this.clearOutput(),
    })
    document.querySelectorAll('[data-input-type]').forEach(button => button.addEventListener('click', () => {
      try { this.setInputType(button.dataset.inputType) } catch (error) { toast(error.message) }
    }))
    $('#text-custom').addEventListener('input', () => { this.count(); this.library.markDirty() })
    $('#dialogue-undo').addEventListener('click', () => this.editor.undoDialogue())
    $('#dialogue-redo').addEventListener('click', () => this.editor.redoDialogue())
    this.drafts = new InputDrafts({ text: '', ssml: '<speak>Hello from Hangry Labs.</speak>',
      serializeMagic: () => this.editor.toSSMLH(), loadMagic: source => this.editor.loadSSMLH(source) })
    this.toolbar = new GenerationToolbar($('#generation-toolbar'))
    this.streamOutput = new AudioEditor($('#stream-output'), { label: 'Streamed audio', onChange: file => { this.outputChanged(file); if (this.resultStreaming) this.sourceEdited(file) } })
    this.finisher = new AudioFinisher($('#generate-finishing'), {
      labels: { processed: 'Processed audio', emptyTitle: 'Processed preview', ready: 'Adjust and create a preview',
        ffmpeg: 'FFmpeg Studio', signalsmith: 'FFmpeg Voice Shape', generateFirst: 'Generate audio first.',
        processFirst: 'Create a processed preview first.', processing: 'Processing with {method}', complete: 'Processed preview ready' },
      responseError: response => this.responseError(response), onError: error => toast(error.message || error),
      onChange: () => { if (!this.restoring && !this.presenting) this.library?.markDirty() },
    })
    this.visualizer = new StreamWaveform($('#stream-live-wave'), $('#stream-live'), $('#stream-live-state'), $('#stream-live-detail'))
    document.querySelectorAll('[data-generation-mode]').forEach(button => button.addEventListener('click', () => this.setGenerationMode(button.dataset.generationMode)))
    $('#stream-stop').addEventListener('click', () => this.controller?.abort())
    $('#markup-guide-button').addEventListener('click', () => $('#markup-guide-dialog').showModal())
    $('#close-markup-guide').addEventListener('click', () => $('#markup-guide-dialog').close())
    closeDialogOnBackdrop($('#markup-guide-dialog'), () => $('#markup-guide-dialog').close())
    for (const id of ['output-format', 'normalize-loudness']) $('#' + id).addEventListener('change', () => this.scheduleAssembly())
    this.setGenerationMode('generate')
    this.showOutput(false)
    this.setInputType('magic', { syncSsmlH: false })
  }

  async initialize() {
    const [capabilities, scripts] = await Promise.all([this.fetchJson('/tts/ssml/capabilities'), this.fetchJson('/tts/dialogue-scripts')])
    this.editor.setCapabilities(capabilities)
    this.editor.setLanguages(['English', 'Chinese', 'Japanese', 'Korean', 'German', 'French', 'Russian', 'Portuguese', 'Spanish', 'Italian'])
    this.library.initialize(scripts.data, scripts.folders)
    await this.refreshVoices()
  }

  async refreshVoices() {
    const data = await this.fetchJson('/tts/voices')
    this.voices = [...data.saved_profiles, ...data.voices]
    this.editor.setVoices(this.voices)
    const previous = $('#saved-voice').value
    $('#saved-voice').replaceChildren(new Option('Built-in', ''), ...data.saved_profiles.map(v => new Option(v.name, v.id)))
    if ([...$('#saved-voice').options].some(o => o.value === previous)) $('#saved-voice').value = previous
    this.defaultVoice()
  }

  defaultVoice() {
    const id = $('#saved-voice').value || $('#speaker').value
    this.editor.setDefaultVoice(this.voices?.find(v => v.id === id) || { id, name: id })
  }

  setInputType(type, { syncSsmlH = true } = {}) {
    if (this.controller) return
    const value = this.drafts.switchTo(type, $('#text-custom').value, { syncSsmlH })
    if (value !== null) $('#text-custom').value = value
    this.inputType = type
    $('#magic-editor-shell').hidden = type !== 'magic'
    $('#text-custom').hidden = type === 'magic'
    document.querySelectorAll('[data-input-type]').forEach(button => {
      button.classList.toggle('active', button.dataset.inputType === type)
      button.setAttribute('aria-pressed', String(button.dataset.inputType === type))
    })
    this.count()
    this.scheduleAssembly()
  }

  count() {
    const text = this.inputType === 'magic' ? this.editor.plainText() : $('#text-custom').value
    $('#text-metrics').textContent = `${text.length} characters · ${text.trim().split(/\s+/).filter(Boolean).length} words`
    return text
  }

  loadExample() {
    const text = 'Good morning! It is a lovely day to give your ideas a voice.'
    if (this.inputType === 'magic') this.loadText(text)
    else {
      const value = this.inputType === 'text' ? text : this.inputType === 'ssml' ? `<speak>${text}</speak>` : serializeMagicDocument([{ type: 'speech', text, prosody: {} }])
      this.drafts.replace(this.inputType, value)
      $('#text-custom').value = value
      this.count(); this.library.markDirty()
    }
  }

  loadText(text) {
    this.editor.loadSSMLH(serializeMagicDocument([{ type: 'speech', text, prosody: {} }]))
  }

  payload() {
    const base = this.options()
    const { speaker, ref_text, xvec_only, mode, ...controls } = base
    return { ...controls, mode: $('#saved-voice').value ? 'clone' : 'custom',
      voice: speaker, voice_profile: $('#saved-voice').value || null,
      text: this.inputType === 'magic' ? this.editor.toSSMLH() : $('#text-custom').value,
      input_type: this.inputType === 'magic' ? 'ssml-h' : this.inputType,
      output_format: $('#output-format').value, speed: Number($('#speech-speed').value),
      normalize_loudness: $('#normalize-loudness').checked, protect_long_audio: $('#protect-long').checked }
  }

  async responseError(response) {
    const data = await response.json().catch(() => ({}))
    return typeof data.detail === 'string' ? data.detail : data.error?.message || `Request failed (${response.status})`
  }

  setGenerationMode(mode) {
    if (this.controller) return
    const format = $('#output-format')
    if (mode === 'stream' && this.generationMode !== 'stream') this.generateFormat = format.value
    if (mode === 'generate' && this.generationMode === 'stream') format.value = this.generateFormat || 'wav'
    if (mode === 'stream') format.value = 'mp3'
    format.disabled = mode === 'stream'
    format.title = mode === 'stream' ? 'Stream preview and download use MP3. Generate uses your selected format.' : ''
    this.generationMode = mode
    $('#streaming').checked = mode === 'stream'
    document.querySelectorAll('[data-generation-mode]').forEach(button => {
      button.classList.toggle('active', button.dataset.generationMode === mode)
      button.setAttribute('aria-pressed', String(button.dataset.generationMode === mode))
    })
    this.scheduleAssembly()
  }

  currentEditor() { return this.resultStreaming ? this.streamOutput : this.outputEditor }
  currentFile() { return this.currentEditor().currentFile() }

  outputChanged(file) {
    $('#use-as-reference').disabled = !file
    $('#save-output').disabled = !file
  }

  sourceEdited(file) {
    if (this.presenting || this.restoring) return
    this.output = file
    if (file) {
      this.outputExtension = file.name.split('.').pop() || 'wav'
      this.finisher.setSource(file, this.outputExtension)
    } else this.finisher.clear()
    this.onOutput(file, this.outputText || this.count(), {})
    this.showOutput(!!file)
    this.library?.markDirty()
  }

  showOutput(visible) {
    $('#generate-finishing').hidden = !visible
    for (const selector of ['#generation-metrics', '#generation-diagnostics', '#generation-actions']) $(selector).hidden = !visible
  }

  async present(blob, extension, text, metrics = {}, { streaming = false, resumeAt = null } = {}) {
    this.output = blob; this.outputExtension = extension; this.resultStreaming = streaming
    this.outputText = text
    let preview = blob, previewExt = extension
    if (extension === 'pcm') {
      const samples = new Int16Array(await blob.arrayBuffer())
      preview = new Blob([encodeWav([Float32Array.from(samples, v => v / 32768)], 24000)], { type: 'audio/wav' })
      previewExt = 'wav'
    }
    const file = new File([preview], 'qwen-dialogue.' + previewExt, { type: preview.type })
    $('#generate-result').hidden = streaming; $('#stream-result').hidden = !streaming
    this.showOutput(true)
    this.finisher.setSource(preview, previewExt)
    this.presenting = true
    try { await this.currentEditor().load(file) } finally { this.presenting = false }
    this.outputChanged(file)
    await this.onOutput(file, text, metrics)
    this.onMetrics(metrics)
    if (resumeAt !== null) await this.currentEditor().playFrom(resumeAt).catch(error => this.toast(error.message))
  }

  clearOutput() {
    clearTimeout(this.assemblyTimer)
    this.assemblyController?.abort(); this.assemblyRevision = (this.assemblyRevision || 0) + 1
    this.output = null; this.outputEditor.clear(); this.streamOutput.clear(); this.finisher.clear(); this.showOutput(false)
    this.onOutput(null, '', {})
  }

  scheduleAssembly() {
    clearTimeout(this.assemblyTimer)
    this.assemblyController?.abort()
    const revision = this.assemblyRevision = (this.assemblyRevision || 0) + 1
    if (!this.library || this.restoring || this.controller || this.inputType !== 'magic' || this.generationMode !== 'generate') return
    if (!this.editor.hasCompleteTakes()) {
      if (this.output) this.clearOutput()
      return
    }
    this.assemblyTimer = setTimeout(async () => {
      const controller = this.assemblyController = new AbortController()
      try {
        const result = await this.takes.assemble(this.editor.blocks, { outputFormat: $('#output-format').value,
          normalizeLoudness: $('#normalize-loudness').checked, signal: controller.signal })
        if (revision !== this.assemblyRevision || this.controller) return
        this.lastCreation = { generatedAt: this.latestTakeGenerationTime, recipe: { version: 1, workflow: 'custom',
          settings: { ...this.payload(), ui_input_type: this.inputType } } }
        await this.present(result.blob, result.extension, this.editor.plainText())
        this.library.markDirty()
      } catch (error) { if (error.name !== 'AbortError') this.toast(error.message) }
    }, 300)
  }

  captureWorkspace() {
    const finishing = this.finisher.snapshot()
    return { settings: { ...this.payload(), ui_input_type: this.inputType, ui_generation_mode: this.generationMode, ui_generate_format: this.generateFormat },
      finishing: { options: finishing.options, processedOptions: finishing.processedOptions, stale: finishing.stale },
      takes: this.inputType === 'magic' ? this.editor.workspaceTakes() : [],
      output: this.output ? { blob: this.output, extension: this.outputExtension } : null, processed: finishing.processed }
  }

  async restoreWorkspace(workspace) {
    this.restoring = true
    try {
      const settings = workspace.settings || {}
      await this.restoreSettings(settings)
      const savedMode = settings.ui_input_type || (['text', 'ssml'].includes(settings.input_type) ? settings.input_type : this.inputType)
      this.setInputType(savedMode, { syncSsmlH: false })
      if (savedMode !== 'magic' && typeof settings.text === 'string') {
        this.drafts.replace(savedMode, settings.text); $('#text-custom').value = settings.text; this.count()
      }
      for (const [key, id] of Object.entries({ temperature: 'temperature', top_k: 'top-k', repetition_penalty: 'repetition',
        chunk_size: 'chunk-size', max_new_tokens: 'max-tokens', output_format: 'output-format', speed: 'speech-speed', language: 'language', instruct: 'custom-instruct' })) {
        if (settings[key] !== undefined) { $('#' + id).value = settings[key]; $('#' + id).dispatchEvent(new Event('input', { bubbles: true })) }
      }
      $('#random-seed').checked = settings.seed == null
      $('#seed').disabled = settings.seed == null
      if (settings.seed != null) $('#seed').value = settings.seed
      $('#text-feed').value = String(settings.non_streaming_mode ?? true)
      $('#protect-long').checked = settings.protect_long_audio ?? true
      $('#normalize-loudness').checked = settings.normalize_loudness ?? false
      this.setGenerationMode(settings.ui_generation_mode || 'generate')
      if (settings.ui_generate_format) this.generateFormat = settings.ui_generate_format
      this.toolbar.sync(); this.defaultVoice()
      this.editor.restoreWorkspaceTakes(workspace.takes)
      if (workspace.output?.blob) {
        this.lastCreation = { generatedAt: null, recipe: { version: 1, workflow: 'custom', settings: structuredClone(settings) } }
        await this.present(workspace.output.blob, workspace.output.extension, this.inputType === 'magic' ? this.editor.plainText() : settings.text || '', {},
          { streaming: this.generationMode === 'stream' })
        await this.finisher.restore({ source: this.finisher.source, processed: workspace.processed, ...workspace.finishing })
      }
    } finally { this.restoring = false }
  }

  progress(phase, title, detail = '') {
    const root = $('#generate-progress')
    root.hidden = false; root.dataset.phase = phase
    root.querySelector('strong').textContent = title; root.querySelector('.progress-copy > span').textContent = detail
    const stages = ['loading_model', 'generating', 'encoding'], index = stages.indexOf(phase === 'streaming' ? 'generating' : phase)
    root.querySelectorAll('[data-stage]').forEach((dot, i) => {
      dot.classList.toggle('active', index === i); dot.classList.toggle('done', phase === 'complete' || index > i)
    })
  }

  async job(callback) {
    if (this.controller) throw new Error('Wait for the current generation or stop it first.')
    clearTimeout(this.assemblyTimer); this.assemblyController?.abort()
    this.assemblyRevision = (this.assemblyRevision || 0) + 1
    this.controller = new AbortController()
    this.onBusy(true, this.controller); this.editor.setBusy(true)
    this.toolbar.close()
    document.querySelectorAll('[data-input-type], [data-generation-mode], .tab-button, #script-new, #script-import, #script-save').forEach(button => { button.disabled = true })
    $('#text-custom').readOnly = true
    $('#stream-stop').hidden = this.generationMode !== 'stream'; $('#stream-stop').disabled = false
    this.progress('preparing', 'Preparing request', 'Checking the script and selected voices')
    try { return await callback(this.controller.signal) }
    catch (error) {
      this.progress('failed', error.name === 'AbortError' ? 'Generation stopped' : 'Generation failed', error.name === 'AbortError' ? 'You can edit and try again.' : error.message)
      throw error
    } finally {
      this.controller = null; this.onBusy(false, null); this.editor.setBusy(false)
      document.querySelectorAll('[data-input-type], [data-generation-mode], .tab-button, #script-new, #script-import, #script-save').forEach(button => { button.disabled = false })
      $('#text-custom').readOnly = false; $('#stream-stop').hidden = true; $('#stream-stop').disabled = true
      this.visualizer.hide()
    }
  }

  async watchProgress(requestId, signal) {
    while (!signal.aborted) {
      try {
        const activity = await this.fetchJson('/tts/activity?request_id=' + encodeURIComponent(requestId), { signal })
        if (activity.phase) this.progress(activity.phase, activity.title, activity.detail)
        await new Promise(resolve => {
          const done = () => { clearTimeout(timer); signal.removeEventListener('abort', done); resolve() }
          const timer = setTimeout(done, 600); signal.addEventListener('abort', done, { once: true })
        })
      } catch { return }
    }
  }

  async generate(streaming) {
    return this.job(async signal => {
      const payload = this.payload(), requestId = generateRequestId()
      const monitor = new AbortController()
      signal.addEventListener('abort', () => monitor.abort(), { once: true })
      const watching = this.watchProgress(requestId, monitor.signal)
      try {
        const compiled = await this.fetchJson('/tts/plan', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload), signal })
        const text = compiled.units.filter(unit => unit.kind === 'speech').map(unit => unit.text).join(' ')
        let blob, extension = payload.output_format, metrics = {}, playback = null, resumeAt = null
        if (this.inputType === 'magic' && !streaming) {
          const result = await this.takes.render(payload, this.editor.blocks, { signal, requestId })
          this.editor.applyTakes(result.takes); this.editor.adoptCommittedProfiles(result.committedProfiles)
          blob = result.output.blob; extension = result.output.extension; metrics = { ...result.metrics, seed: result.requestSeed }
        } else if (streaming) {
          // MP3 provides progressive browser playback. The final player retains
          // the exact streamed recording, without a second inference request.
          extension = 'mp3'
          this.visualizer.surface.hidden = false; this.visualizer.drawIdle(); this.visualizer.update(0)
          playback = await IncrementalAudioPlayback.create(this.visualizer, { signal })
          signal.throwIfAborted()
          const abortPlayback = () => playback?.stop()
          signal.addEventListener('abort', abortPlayback, { once: true })
          try {
            const response = await fetch('/tts/stream', { method: 'POST', headers: { 'Content-Type': 'application/json', 'X-Qwen-Request-ID': requestId },
              body: JSON.stringify({ ...payload, stream_format: 'mp3' }), signal })
            if (!response.ok) throw new Error(await this.responseError(response))
            metrics.seed = Number(response.headers.get('X-Qwen-Seed'))
            const reader = response.body.getReader(), chunks = []; let size = 0
            for (;;) {
              const { value, done } = await reader.read()
              if (done) break
              chunks.push(value); size += value.length
              if (playback) await playback.append(value)
              this.visualizer.update(size, playback?.currentTime() || 0)
            }
            signal.throwIfAborted()
            if (!size) throw new Error('The stream ended without audio.')
            await playback?.finish()
            resumeAt = playback?.currentTime() ?? 0
            blob = new Blob(chunks, { type: 'audio/mpeg' })
          } finally { signal.removeEventListener('abort', abortPlayback); playback?.stop() }
          const activity = await this.fetchJson('/tts/activity?request_id=' + requestId, { signal })
          metrics = { ...metrics, ...activity.metrics }
          this.editor.adoptCommittedProfiles(activity.committed_profiles || {})
        } else {
          const response = await fetch('/tts/generate', { method: 'POST', headers: { 'Content-Type': 'application/json', 'X-Qwen-Request-ID': requestId }, body: JSON.stringify(payload), signal })
          if (!response.ok) throw new Error(await this.responseError(response))
          blob = await response.blob(); metrics = { ...JSON.parse(response.headers.get('X-Qwen-Metrics') || '{}'), seed: Number(response.headers.get('X-Qwen-Seed')) }
          this.editor.adoptCommittedProfiles(JSON.parse(response.headers.get('X-Qwen-Committed-Profiles') || '{}'))
        }
        monitor.abort(); await watching
        signal.throwIfAborted()
        this.progress('encoding', 'Preparing the player', 'Decoding the completed recording')
        this.lastCreation = { generatedAt: performance.now(), recipe: { version: 1, workflow: 'custom',
          settings: { ...structuredClone(payload), seed: metrics.seed, randomize_seed: false,
            ui_input_type: this.inputType, ui_generation_mode: this.generationMode,
            ui_generate_format: this.generateFormat } } }
        await this.present(blob, extension, text, metrics, { streaming, resumeAt })
        $('#last-generated-seed').value = metrics.seed ?? ''; this.toolbar.sync()
        this.progress('complete', 'Generation complete', streaming ? 'MP3 stream ready to replay or finish' : 'Audio ready to play, save or finish')
        this.library.markDirty(); await this.refreshVoices()
      } finally { monitor.abort(); await watching }
    })
  }
}
