// Qwen workflow adapter for the Apache-2.0 VoxCPMTTS UI components; see NOTICE.
import { initializeI18n } from './i18n.js'
import { AudioEditor } from './audio-editor.js'
import { AudioRecorder } from './audio-recorder.js'
import { GpuMonitor } from './gpu-monitor.js'
import { encodeWav } from './audio-utils.js'
import { decodePcmWav, PcmPlayer } from './pcm-player.js'
import { closeDialogOnBackdrop } from './dialog-utils.js'
import { GenerateWorkbench } from './generate-workbench.js'
import { VoiceLibrary, refinementDocument } from './voice-library.js'

const $ = (selector) => document.querySelector(selector)
const $$ = (selector) => [...document.querySelectorAll(selector)]
const state = { tab: 'custom', mode: 'custom', capabilities: null, busy: false,
  controller: null, player: null, outputs: {}, models: {}, textFeed: {}, toastTimer: null }
const names = { custom: 'Generate speech', design: 'Design voice', clone: 'Clone voice' }
const examples = {
  custom: 'Good morning! It is a lovely day to give your ideas a voice.',
  design: 'Welcome to our little corner of the world. Take a breath, settle in, and let the story begin.',
  clone: 'This is a new sentence, spoken with the voice from my reference recording.',
}

function toast(message) {
  $('#toast').textContent = String(message)
  $('#toast').hidden = false
  clearTimeout(state.toastTimer)
  state.toastTimer = setTimeout(() => { $('#toast').hidden = true }, 7000)
}

async function fetchJson(path, options = {}) {
  const response = await fetch(path, { cache: 'no-store', ...options })
  const data = await response.json()
  if (!response.ok) throw new Error(typeof data.detail === 'string' ? data.detail : JSON.stringify(data.detail || data))
  return data
}

function selectOptions(select, items, value = null) {
  select.replaceChildren(...items.map((item) => {
    const option = document.createElement('option')
    option.value = typeof item === 'string' ? item : item.id
    option.textContent = typeof item === 'string' ? item : item.label
    if (select.id === 'model') option.textContent = option.textContent.replace('CustomVoice', 'Custom').replace('VoiceDesign', 'Design').replace('-', ' ')
    option.title = typeof item === 'string' ? item : item.label
    return option
  }))
  if (value && [...select.options].some((item) => item.value === value)) select.value = value
}

const reference = new AudioEditor($('#reference-editor'), { label: 'Reference audio',
  emptyTitle: 'Your voice reference', emptyDescription: 'Upload, record, or use a designed voice',
  onChange: (file) => {
    $('#transcribe-reference').disabled = !file
    $('#save-reference').disabled = !file
    $('#reference-text').value = ''
  } })
const output = new AudioEditor($('#output-editor'), { label: 'Generated audio',
  emptyTitle: 'Your voice, ready to hear', emptyDescription: 'Generated speech appears here',
  onChange: (file) => {
    $('#use-as-reference').disabled = !file
    $('#save-output').disabled = !file
    if (state.capabilities && state.mode === 'custom' && !workbench.resultStreaming) workbench.sourceEdited(file)
  } })
for (const editor of [reference, output]) editor.container.addEventListener('audio-error', (event) => toast(event.detail?.message || 'Unable to load audio.'))
const recorder = new AudioRecorder({ button: $('#record-reference'), status: $('#recording-status'),
  canvas: $('#recording-canvas'), deviceSelect: $('#microphone-device'), refreshButton: $('#refresh-microphones'),
  onFile: (file) => loadReference(file), onError: (error) => toast(error.message),
  labels: { ready: 'Microphone ready', record: 'Record', stop: 'Stop recording', recording: 'Recording {time}',
    processing: 'Preparing recording', readyWithTime: 'Recorded {time}', unavailable: 'Recording needs microphone permission and localhost or HTTPS.' } })
const gpu = new GpuMonitor($('#gpu-output'), { fetchJson })

async function loadReference(file) {
  if (file.size > (state.capabilities?.max_upload_bytes || 10 * 1024 * 1024)) throw new Error('Choose reference audio smaller than 10 MB.')
  await reference.load(file)
}

function updateCount() {
  $('#text-count').textContent = state.mode === 'custom' ? `${workbench.count().length} input characters` : `${$(`#text-${state.mode}`).value.length} / 1000 characters`
}

function updateModelControls() {
  if (!state.capabilities) return
  const spec = state.capabilities.models.find((item) => item.id === $('#model').value)
  $('#speaker-field').hidden = state.mode !== 'custom' || !!$('#saved-voice').value
  $('#custom-instruction-field').hidden = state.mode !== 'custom' || !spec?.instructions
  $('#custom-instruction-help').hidden = state.mode !== 'custom' || !!spec?.instructions
  $('#clone-instruction-field').hidden = state.mode !== 'clone' || !spec?.instructions
  updateCloneGuidance()
  $('#model-help').textContent = spec?.mode === 'design' ? 'Creates a new voice from a description.' : spec?.mode === 'clone' ? 'Recreates a voice from reference audio.' : 'Nine built-in speakers. The 1.7B model also supports style instructions.'
  state.models[state.mode] = $('#model').value
  $('#model').title = spec?.label || $('#model').value
  workbench.defaultVoice()
}

function updateCloneGuidance() {
  const identityOnly = $('#clone-method').value === 'true'
  $('#transcript-required').textContent = identityOnly ? '(optional for speaker identity only)' : '(required)'
  $('#clone-instruction-help').textContent = identityOnly
    ? 'Delivery direction is experimental. Choose Speaker and reference transcript for best results; speaker identity only may ignore the direction. Leave blank to clone without direction.'
    : 'Delivery direction is experimental. The reference audio and its exact transcript help guide the delivery. Results vary by voice and instruction; leave blank to clone without direction.'
}

function renderMetrics(metrics) {
  const panel = $('#generation-metrics')
  panel.replaceChildren()
  for (const [label, value] of [
    ['Audio', `${Number(metrics.duration_s || 0).toFixed(2)} s`],
    ['First audio', `${Number(metrics.ttfa_ms || 0).toFixed(0)} ms`],
    ['Generation', `${(Number(metrics.generation_ms || 0) / 1000).toFixed(2)} s`],
    ['Realtime speed', `${Number(metrics.speed || 0).toFixed(2)}×`],
  ]) {
    const span = document.createElement('span'), strong = document.createElement('strong')
    strong.textContent = value; span.append(strong, label); panel.append(span)
  }
  renderDiagnostics(metrics)
}

function renderDiagnostics(metrics) {
  const ms = value => value == null ? 'Not available' : `${Number(value).toFixed(0)} ms`
  const rows = [
    ['Queue wait', ms(metrics.queue_ms)], ['Model loading', ms(metrics.model_load_ms)],
    ['Reference preparation', ms(metrics.reference_preparation_ms)],
    ['Reference cache', metrics.reference_cache_hit == null ? 'Not applicable' : metrics.reference_cache_hit ? 'Reused' : 'Prepared'],
    ['Server first audio', ms(metrics.ttfa_ms)], ['Model TTFA (streaming)', ms(metrics.model_ttfa_ms)],
    ['Model generation (streaming)', ms(metrics.model_generation_ms)],
    ['First chunk received', ms(metrics.client_first_chunk_ms)],
    ['Playback start (scheduled)', ms(metrics.client_playback_ms)],
    ['Playback buffered ahead', `${Number(metrics.buffered_s || 0).toFixed(2)} s`],
    ['Server total, including queue', ms(metrics.total_ms)],
  ]
  $('#diagnostic-values').replaceChildren(...rows.flatMap(([name, value]) => {
    const label = document.createElement('dt'), result = document.createElement('dd')
    label.textContent = name; result.textContent = value
    return [label, result]
  }))
}

function updateChunkHelp() {
  const frames = Number($('#chunk-size').value), limits = state.capabilities?.chunk_size
  $('#chunk-size-help').textContent = Number.isInteger(frames) && frames >= (limits?.min || 1) && frames <= (limits?.max || 64)
    ? `${frames} frame${frames === 1 ? '' : 's'} ≈ ${(frames / 12).toFixed(2)} seconds of audio. Smaller chunks reduce the wait for first audio.`
    : `Choose a whole number from ${limits?.min || 1} to ${limits?.max || 64}.`
}

async function activateTab(tab) {
  const changed = tab !== state.tab
  if (changed && state.busy) return
  if (changed && state.capabilities) {
    if (state.outputs[state.mode]) state.outputs[state.mode].finishing = workbench.finisher.snapshot()
    output.wave.pause(); workbench.streamOutput.wave.pause(); workbench.finisher.output.wave.pause()
    $('#generate-progress').hidden = true
  }
  if (state.capabilities && ['custom', 'design', 'clone'].includes(state.tab)) state.textFeed[state.mode] = $('#text-feed').value === 'true'
  state.tab = tab
  history.replaceState(null, '', location.pathname + location.search + '#' + tab)
  const workflow = ['custom', 'design', 'clone'].includes(tab)
  if (workflow) state.mode = tab
  $('.workspace').dataset.view = tab
  $$('.tab-button').forEach((button) => {
    const selected = button.dataset.tab === tab
    button.classList.toggle('active', selected)
    button.setAttribute('aria-selected', String(selected))
    button.tabIndex = selected ? 0 : -1
  })
  $('#inference-settings').hidden = !workflow
  $('#workflow-content').hidden = !workflow
  $('#api-view').hidden = tab !== 'api'
  $('#system-view').hidden = tab !== 'system'
  $('#voices-view').hidden = tab !== 'voices'
  $('.script-library').hidden = tab !== 'custom'
  $('#saved-voice-field').hidden = tab !== 'custom'
  $('#output-format-field').hidden = tab !== 'custom'
  // Sampling, seed and finishing controls remain available in every workflow.
  const toolbar = $('#generation-toolbar')
  $('#generate-authoring').hidden = tab !== 'custom'
  const parent = tab === 'custom' ? $('#generate-primary') : $('#workflow-content')
  parent.append($('#result-panel'), $('#stream-surface'))
  if (tab === 'custom') $('[data-workflow=custom]').insertBefore(toolbar, $('#magic-editor-shell'))
  else if (workflow) $('#workflow-content').prepend(toolbar)
  toolbar.hidden = !workflow
  $$('.workflow-pane').forEach((panel) => { panel.hidden = panel.dataset.workflow !== state.mode })
  if (workflow && state.capabilities) {
    const modelMode = tab === 'custom' && $('#saved-voice').value ? 'clone' : state.mode
    const choices = state.capabilities.models.filter(item => item.mode === modelMode)
    const selected = choices.some(item => item.id === state.models[state.mode]) ? state.models[state.mode] : state.capabilities.workflow_defaults[modelMode].model
    selectOptions($('#model'), choices, selected)
    updateModelControls()
    $('#text-feed').value = String(state.textFeed[state.mode] ?? state.capabilities.workflow_defaults[state.mode].non_streaming_mode)
    $('#generate-button span').textContent = state.busy ? 'Stop generation' : names[state.mode]
    const saved = state.outputs[state.mode]
    if (tab === 'custom') {
      $('#generate-result').hidden = workbench.resultStreaming || !saved
      $('#stream-result').hidden = !workbench.resultStreaming
      workbench.showOutput(!!saved)
      if (saved && !workbench.resultStreaming && output.currentFile() !== saved.file) {
        workbench.presenting = true
        try { await output.load(saved.file) } finally { workbench.presenting = false }
      }
      if (saved) renderMetrics(saved.metrics)
    } else {
      $('#generate-result').hidden = false; $('#stream-result').hidden = true
      workbench.showOutput(!!saved)
      if (saved) { await output.load(saved.file); renderMetrics(saved.metrics) }
      else if (!state.busy) { output.clear(); renderDiagnostics({}) }
    }
    if (changed && saved?.finishing) await workbench.finisher.restore(saved.finishing)
    workbench.toolbar.sync()
  }
  updateCount()
  if (tab === 'system' && !document.hidden) { gpu.start(); refreshAsr().catch(() => {}) }
  else gpu.stop()
  try { sessionStorage.setItem('qwen3tts-ui-state-v1', JSON.stringify({ tab, headerCollapsed: $('#brand-hero').dataset.collapsed === 'true' })) } catch {}
}

function example(mode) {
  if (mode === 'custom') { workbench.loadExample(); updateCount(); return }
  $(`#text-${mode}`).value = examples[mode]
  if (mode === 'design') $('#design-instruct').value = 'A warm female narrator with a clear, gentle voice and a relaxed, conversational delivery.'
  updateCount()
}

function requestOptions() {
  const mode = state.mode
  const spec = state.capabilities.models.find((item) => item.id === $('#model').value)
  return { mode, model: $('#model').value, text: $(`#text-${mode}`).value.trim(), language: $('#language').value,
    speaker: $('#speaker').value || 'Ryan', instruct: mode === 'design' ? $('#design-instruct').value.trim() : spec.instructions ? $(`#${mode}-instruct`).value.trim() : '',
    ref_text: $('#reference-text').value.trim(), xvec_only: $('#clone-method').value === 'true',
    non_streaming_mode: $('#text-feed').value === 'true', temperature: Number($('#temperature').value),
    top_k: Number($('#top-k').value), repetition_penalty: Number($('#repetition').value),
    chunk_size: Number($('#chunk-size').value), max_new_tokens: Number($('#max-tokens').value),
    seed: $('#random-seed').checked ? null : Number($('#seed').value) }
}

function bytesFromBase64(encoded) {
  return Uint8Array.from(atob(encoded), (character) => character.charCodeAt(0))
}

function drawStream(samples) {
  const canvas = $('#stream-canvas'), ctx = canvas.getContext('2d'), ratio = devicePixelRatio || 1
  canvas.width = Math.max(1, canvas.clientWidth * ratio); canvas.height = 70 * ratio
  ctx.clearRect(0, 0, canvas.width, canvas.height); ctx.strokeStyle = '#ff7a1a'; ctx.lineWidth = 2 * ratio
  ctx.beginPath()
  const bars = Math.max(1, Math.floor(canvas.width / (4 * ratio)))
  for (let index = 0; index < bars; index++) {
    const start = Math.floor(index / bars * samples.length), end = Math.floor((index + 1) / bars * samples.length)
    let peak = .02
    for (let frame = start; frame < end; frame++) peak = Math.max(peak, Math.abs(samples[frame]))
    const x = (index + .5) / bars * canvas.width, height = Math.min(.95, peak * 2) * canvas.height * .45
    ctx.moveTo(x, canvas.height / 2 - height); ctx.lineTo(x, canvas.height / 2 + height)
  }
  ctx.stroke()
}

async function readSse(response, onEvent) {
  const reader = response.body.getReader(), decoder = new TextDecoder()
  let pending = ''
  while (true) {
    const { done, value } = await reader.read()
    pending += decoder.decode(value || new Uint8Array(), { stream: !done }).replaceAll('\r\n', '\n')
    let boundary
    while ((boundary = pending.indexOf('\n\n')) >= 0) {
      const frame = pending.slice(0, boundary); pending = pending.slice(boundary + 2)
      for (const line of frame.split('\n')) if (line.startsWith('data: ')) await onEvent(JSON.parse(line.slice(6)))
    }
    if (done) break
  }
}

async function generate() {
  if (state.busy) {
    state.controller?.abort()
    state.player?.stop().catch(() => {})
    return
  }
  if (state.mode === 'custom') {
    try { await workbench.generate($('#streaming').checked) }
    catch (error) { toast(error.name === 'AbortError' ? 'Generation stopped' : error.message) }
    finally { refreshStatus().catch(() => {}) }
    return
  }
  const options = requestOptions(), mode = options.mode, streaming = $('#streaming').checked
  if (options.seed == null) options.seed = crypto.getRandomValues(new Uint32Array(1))[0]
  const sourceReference = mode === 'clone' ? reference.currentFile() : null
  const chunkLimits = state.capabilities.chunk_size
  if (!Number.isInteger(options.chunk_size) || options.chunk_size < chunkLimits.min || options.chunk_size > chunkLimits.max) return toast(`Choose a whole chunk size from ${chunkLimits.min} to ${chunkLimits.max}.`)
  if (!options.text) return toast('Enter text to speak.')
  if (mode === 'design' && !options.instruct) return toast('Describe the voice you want to create.')
  if (mode === 'clone' && !reference.currentFile()) return toast('Choose or record a reference first.')
  if (mode === 'clone' && !options.xvec_only && !options.ref_text) return toast('Add the exact reference transcript, or use Transcribe reference.')
  const form = new FormData()
  form.set('options', JSON.stringify(options))
  if (mode === 'clone') form.set('reference', reference.currentFile())
  state.busy = true; state.controller = new AbortController()
  $('#generate-button span').textContent = 'Stop generation'
  $('#generate-button').dataset.running = 'true'
  $('#stream-surface').hidden = !streaming
  $('#stream-state').textContent = 'Preparing model and waiting for speech'
  $('#stream-detail').textContent = ''
  $('#global-status').textContent = 'Loading model or waiting for inference'
  $('#request-status').hidden = false
  $('#request-status').textContent = 'Submitting request'
  const chunks = []; let rate = 24000, metrics = {}, completed = false
  const clientMetrics = { buffered_s: 0 }
  let diagnosticsTimer = null
  try {
    if (streaming && window.AudioContext) { state.player = new PcmPlayer(); await state.player.resume() }
    const requestStarted = performance.now()
    renderDiagnostics({})
    diagnosticsTimer = setInterval(() => {
      clientMetrics.buffered_s = state.player?.bufferedSeconds() || 0
      renderDiagnostics({ ...metrics, ...clientMetrics })
    }, 250)
    // Progress events also surround complete inference; playback streaming stays independent.
    const response = await fetch('/studio/generate/stream' + (streaming ? '' : '?streaming=false'), {
      method: 'POST', body: form, signal: state.controller.signal,
    })
    if (!response.ok) { const data = await response.json(); throw new Error(data.detail || 'Generation failed.') }
    await readSse(response, async (event) => {
        if (event.type === 'error') throw new Error(event.message)
        if (event.type === 'queued') {
          $('#request-status').textContent = event.position > 0 ? `Waiting for inference: ${event.position} request${event.position === 1 ? '' : 's'} ahead` : 'Preparing model and voice'
          $('#global-status').textContent = $('#request-status').textContent
        }
        if (event.type === 'loading') $('#request-status').textContent = 'Loading the selected model'
        if (event.type === 'ready') { $('#stream-state').textContent = 'Generating speech'; $('#request-status').textContent = 'Generating speech' }
        if (event.type === 'chunk') {
          if (clientMetrics.client_first_chunk_ms == null) clientMetrics.client_first_chunk_ms = performance.now() - requestStarted
          const decoded = decodePcmWav(bytesFromBase64(event.audio_b64))
          rate = decoded.rate; chunks.push(decoded.samples)
          const scheduledAt = state.player?.play(decoded.samples, rate)
          if (scheduledAt != null && clientMetrics.client_playback_ms == null) clientMetrics.client_playback_ms = scheduledAt - requestStarted
          clientMetrics.buffered_s = state.player?.bufferedSeconds() || 0
          metrics = event.metrics || metrics
          renderMetrics({ ...metrics, ...clientMetrics })
          if (streaming) drawStream(decoded.samples)
          $('#stream-state').textContent = streaming ? 'Playing generated speech' : 'Preparing complete audio'
          $('#stream-detail').textContent = `${event.duration_s.toFixed(2)} seconds received`
        }
        if (event.type === 'done') { metrics = event.metrics; completed = true; renderMetrics({ ...metrics, ...clientMetrics }) }
      })
    if (!completed) throw new Error('The audio response ended before completion.')
    const count = chunks.reduce((sum, chunk) => sum + chunk.length, 0), all = new Float32Array(count)
    let offset = 0
    chunks.forEach((chunk) => { all.set(chunk, offset); offset += chunk.length })
    const file = new File([encodeWav([all], rate)], `qwen-${mode}-${Date.now()}.wav`, { type: 'audio/wav' })
    state.outputs[mode] = { file, text: options.text, metrics: { ...metrics, ...clientMetrics, seed: options.seed },
      recipe: { version: 1, workflow: mode, settings: structuredClone(options) },
      source: sourceReference, generatedAt: performance.now() }
    $('#last-generated-seed').value = options.seed; workbench.toolbar.sync()
    if (state.mode === mode && ['custom','design','clone'].includes(state.tab)) {
      workbench.showOutput(true)
      $('#generate-result').hidden = false; $('#stream-result').hidden = true
      workbench.finisher.setSource(file, 'wav')
      await output.load(file); renderMetrics({ ...metrics, ...clientMetrics })
    }
    $('#stream-state').textContent = 'Generation complete'
    $('#global-status').textContent = 'Speech generated'
    if (state.player) await state.player.finish()
    $('#request-status').textContent = 'Generation complete'
  } catch (error) {
    if (error.name === 'AbortError') { $('#stream-state').textContent = 'Generation stopped'; $('#global-status').textContent = 'Stopped'; $('#request-status').textContent = 'Generation stopped' }
    else { toast(error.message); $('#global-status').textContent = 'Generation failed'; $('#stream-state').textContent = 'Generation failed'; $('#request-status').textContent = error.message }
  } finally {
    clearInterval(diagnosticsTimer)
    await state.player?.stop().catch(() => {})
    clientMetrics.buffered_s = 0
    if (completed && state.outputs[mode]) {
      state.outputs[mode].metrics = { ...metrics, ...clientMetrics }
    }
    renderDiagnostics({ ...metrics, ...clientMetrics })
    state.player = null; state.controller = null; state.busy = false
    $('#generate-button span').textContent = names[state.mode]
    $('#generate-button').dataset.running = 'false'
    refreshStatus().catch(() => {})
  }
}

async function refreshStatus() {
  const status = await fetchJson('/studio/status')
  const label = { idle: 'Ready to load a voice', ready: 'Inference ready', loading: 'Loading model', generating: 'Generating speech', error: 'Inference needs attention' }[status.state] || status.state
  $('#runtime-state').textContent = label
  const activeModel = status.model?.split('/').at(-1)?.replace('Qwen3-TTS-12Hz-', '')
  $('#runtime-model').textContent = activeModel ? `${activeModel}${status.resident_models?.length > 1 ? ' · ' + status.resident_models.length + ' loaded' : ''}` : 'NVIDIA · models load on demand'
  $('#runtime-badge').dataset.state = status.state === 'ready' ? 'ready' : status.state === 'error' ? 'error' : status.state === 'idle' ? 'ready' : 'starting'
  const resident = status.resident_models || (status.model ? [status.model] : [])
  $('#residency-status').textContent = `${resident.length ? 'In memory: ' + resident.map(id => id.split('12Hz-').at(-1)).join(', ') : 'No weights in memory'}${status.error ? ' · ' + status.error : ''}`
  const errors = Object.entries(status.residency_errors || {}).map(([id, error]) => `${id.split('12Hz-').at(-1)}: ${error}`)
  if (errors.length) $('#model-policy-status').textContent = errors.join(' · ')
  if (!state.busy) $('#global-status').textContent = label
}

async function refreshAsr() {
  $('#asr-status').textContent = 'Checking connection'
  const result = await fetchJson('/studio/asr/status')
  $('#asr-status').textContent = result.ready ? 'Qwen3 ASR is ready' : 'ASR is not ready. Check the URL and service.'
}

async function refreshVoices() {
  await voiceLibrary.refresh()
}

function openSave(file, transcript, context = null) {
  voiceLibrary.open(file, transcript, context)
}

function captureVoice() {
  const generated = state.outputs[state.mode] || {}
  const finishing = workbench.finisher.snapshot()
  return { ...generated, original: state.mode === 'custom' ? workbench.currentFile() : output.currentFile(),
    finishing, recipe: generated.recipe || { workflow: state.mode, settings: requestOptions() } }
}

async function voiceFile(url, name = 'reference.wav') {
  const response = await fetch(url, { cache: 'no-store' })
  if (!response.ok) throw new Error('Saved voice audio could not be loaded.')
  return new File([await response.blob()], name, { type: 'audio/wav' })
}

async function refineVoice(profile) {
  const recipe = structuredClone(profile.recipe || {}), settings = recipe.settings || {}
  const mode = ['custom', 'design', 'clone'].includes(recipe.workflow) ? recipe.workflow : 'clone'
  // Load every asset before changing the current workspace so a failed read leaves it intact.
  const [original, processed, source] = await Promise.all([
    voiceFile(profile.original_url || profile.audio_url),
    profile.processed_url ? voiceFile(profile.processed_url, 'processed.wav') : null,
    profile.source_url ? voiceFile(profile.source_url, 'source.wav') : mode === 'clone' ? voiceFile(profile.audio_url) : null,
  ])
  if (mode === 'custom') {
    if (settings.ui_input_type === 'magic' || settings.input_type === 'ssml-h') {
      settings.text = refinementDocument(settings.text || '', voiceLibrary.records.map(voice => voice.name))
    }
    if (settings.ui_input_type === 'magic') workbench.editor.loadSSMLH(settings.text || '')
    await workbench.restoreWorkspace({ settings, output: { blob: original, extension: 'wav' },
      processed: processed ? { blob: processed, extension: 'wav' } : null, finishing: recipe.finishing })
  } else {
    if (settings.model) state.models[mode] = settings.model
    await activateTab(mode)
    for (const [key, id] of Object.entries({ language: 'language', temperature: 'temperature', top_k: 'top-k',
      repetition_penalty: 'repetition', chunk_size: 'chunk-size', max_new_tokens: 'max-tokens' })) {
      if (settings[key] != null) { $('#' + id).value = settings[key]; $('#' + id).dispatchEvent(new Event('input', { bubbles: true })) }
    }
    $(`#text-${mode}`).value = settings.text || profile.ref_text || ''
    $(`#${mode}-instruct`).value = settings.instruct || ''
    $('#random-seed').checked = settings.seed == null; $('#seed').disabled = settings.seed == null
    if (settings.seed != null) $('#seed').value = settings.seed
    $('#text-feed').value = String(settings.non_streaming_mode ?? mode !== 'clone')
    if (mode === 'clone') {
      await reference.load(source)
      $('#reference-text').value = settings.ref_text ?? profile.ref_text ?? ''
      $('#clone-method').value = String(settings.xvec_only ?? !$('#reference-text').value)
      updateCloneGuidance()
    }
    await output.load(original); workbench.showOutput(true)
    await workbench.finisher.restore({ source: { blob: original, extension: 'wav' },
      processed: processed ? { blob: processed, extension: 'wav' } : null, ...recipe.finishing })
  }
  state.outputs[mode] = { file: original, text: settings.text || profile.ref_text || '',
    recipe: structuredClone(recipe), source, generatedAt: null, metrics: { seed: settings.seed },
    finishing: workbench.finisher.snapshot() }
  updateCount(); workbench.toolbar.sync()
  toast(`Refining ${profile.name}. Generate a new recording to enable replacement; the saved voice remains available.`)
}

async function setHeaderCollapsed(collapsed, animate = true) {
  const hero = $('#brand-hero'), start = hero.getBoundingClientRect().height
  const reduced = matchMedia('(prefers-reduced-motion: reduce)').matches
  hero.dataset.collapsed = String(collapsed)
  document.documentElement.dataset.headerCollapsed = String(collapsed)
  $('#hero-toggle').setAttribute('aria-expanded', String(!collapsed))
  $('#hero-toggle').setAttribute('aria-label', collapsed ? 'Expand header' : 'Collapse header')
  $('#hero-toggle').title = collapsed ? 'Expand header' : 'Collapse header'
  $('#hero-toggle i').className = collapsed ? 'icon-chevron-down' : 'icon-chevron-up'
  const end = hero.getBoundingClientRect().height
  if (animate && !reduced) hero.animate([{ height: start + 'px' }, { height: end + 'px' }], { duration: 180, easing: 'ease-out' })
  try { sessionStorage.setItem('qwen3tts-ui-state-v1', JSON.stringify({ tab: state.tab, headerCollapsed: collapsed })) } catch {}
}

const workbench = new GenerateWorkbench({ options: requestOptions, fetchJson, toast, onMetrics: renderMetrics, outputEditor: output,
  saveVoice: openSave,
  restoreSettings: async settings => {
    $('#saved-voice').value = settings.voice_profile || ''
    if (settings.model) state.models.custom = settings.model
    await activateTab('custom')
    if (settings.voice) $('#speaker').value = settings.voice
  },
  onBusy: (busy, controller) => {
    state.busy = busy; state.controller = controller
    $('#generate-button span').textContent = busy ? 'Stop generation' : names[state.mode]
    $('#generate-button').dataset.running = String(busy)
  },
  onOutput: async (file, text, metrics) => {
    const created = workbench.lastCreation
    state.outputs.custom = { file, text, metrics,
      recipe: created?.recipe, generatedAt: created?.generatedAt }
    if (!file) delete state.outputs.custom
  },
})
const voiceLibrary = new VoiceLibrary({ fetchJson, toast, capture: captureVoice,
  isBusy: () => state.busy,
  onRefresh: async () => {
    const selected = $('#saved-voice').value
    await workbench.refreshVoices()
    if (selected !== $('#saved-voice').value && state.capabilities && state.tab === 'custom') await activateTab('custom')
  },
  onUse: async profile => {
    await activateTab('custom'); $('#saved-voice').value = profile.id
    await activateTab('custom'); workbench.defaultVoice()
  },
  onRefine: refineVoice,
})
window.addEventListener('voice-library-changed', () => refreshVoices().catch(error => toast(error.message)))
$$('[data-open-voices]').forEach(button => button.addEventListener('click', () => activateTab('voices')))
$('#saved-voice').addEventListener('change', () => activateTab('custom').catch(error => toast(error.message)))
$('#speaker').addEventListener('change', () => workbench.defaultVoice())
$('#generate-button').addEventListener('click', () => generate().catch((error) => toast(error.message)))
$$('.tab-button').forEach((button) => button.addEventListener('click', () => activateTab(button.dataset.tab).catch((error) => toast(error.message))))
$('.app-tabs').addEventListener('keydown', (event) => {
  const buttons = $$('.tab-button'), current = buttons.indexOf(document.activeElement)
  if (current < 0 || !['ArrowLeft', 'ArrowRight', 'Home', 'End'].includes(event.key)) return
  event.preventDefault()
  const next = event.key === 'Home' ? 0 : event.key === 'End' ? buttons.length - 1 : (current + (event.key === 'ArrowRight' ? 1 : -1) + buttons.length) % buttons.length
  buttons[next].focus(); buttons[next].click()
})
$('#model').addEventListener('change', updateModelControls)
$$('textarea[id^=text-]').forEach((input) => input.addEventListener('input', updateCount))
$$('[data-example]').forEach((button) => button.addEventListener('click', () => example(button.dataset.example)))
$('#examples-button').addEventListener('click', (event) => { event.preventDefault(); if (!['custom','design','clone'].includes(state.tab)) activateTab('design'); example(state.mode) })
$('#models-button').addEventListener('click', (event) => { event.preventDefault(); activateTab('system'); $('#policy-model-custom')?.focus() })
$$('[data-number]').forEach((slider) => {
  const number = $('#' + slider.dataset.number)
  slider.addEventListener('input', () => { number.value = slider.value })
  number.addEventListener('input', () => { slider.value = number.value })
})
$('#random-seed').addEventListener('change', () => { $('#seed').disabled = $('#random-seed').checked })
$('#reset-controls').addEventListener('click', () => {
  for (const [id, value] of [['temperature',.9],['top-k',50],['repetition',1.05]]) { $('#' + id).value = value; $(`[data-number="${id}"]`).value = value }
  $('#chunk-size').value = '8'; $('#chunk-size-slider').value = '8'; updateChunkHelp(); $('#max-tokens').value = '360'
  $('#text-feed').value = String(state.capabilities.workflow_defaults[state.mode].non_streaming_mode)
  state.textFeed[state.mode] = $('#text-feed').value === 'true'
  $('#random-seed').checked = true; $('#seed').disabled = true
  $('#speech-speed').value = '1'; $('#protect-long').checked = true; $('#normalize-loudness').checked = false
  workbench.toolbar.sync()
})
$('#clone-method').addEventListener('change', updateCloneGuidance)
$('#chunk-size').addEventListener('input', updateChunkHelp)
$('#chunk-size-slider').addEventListener('input', updateChunkHelp)
$('#reference-drop').addEventListener('click', () => $('#reference-file').click())
$('#reference-drop').addEventListener('keydown', (event) => { if (['Enter',' '].includes(event.key)) { event.preventDefault(); $('#reference-file').click() } })
$('#reference-file').addEventListener('change', async (event) => { if (event.target.files[0]) { try { await loadReference(event.target.files[0]) } catch (error) { toast(error.message) } } event.target.value = '' })
for (const event of ['dragenter','dragover']) $('#reference-drop').addEventListener(event, (e) => { e.preventDefault(); $('#reference-drop').classList.add('dragging') })
for (const event of ['dragleave','drop']) $('#reference-drop').addEventListener(event, (e) => { e.preventDefault(); $('#reference-drop').classList.remove('dragging') })
$('#reference-drop').addEventListener('drop', (event) => { const file = event.dataTransfer.files[0]; if (file) loadReference(file).catch((error) => toast(error.message)) })
$('#transcribe-reference').addEventListener('click', async () => {
  if (!reference.currentFile()) return
  const button = $('#transcribe-reference'); button.disabled = true; button.textContent = 'Transcribing…'
  try { const form = new FormData(); form.set('file', reference.currentFile()); const result = await fetchJson('/studio/asr/transcribe', { method: 'POST', body: form }); $('#reference-text').value = result.text }
  catch (error) { toast(error.message) }
  finally { button.disabled = !reference.currentFile(); button.textContent = 'Transcribe reference' }
})
$('#use-as-reference').addEventListener('click', async () => { const file = state.mode === 'custom' ? workbench.currentFile() : output.currentFile(); if (!file) return; const saved = state.outputs[state.mode]; await reference.load(file); $('#reference-text').value = saved?.text || ''; await activateTab('clone') })
$('#save-output').addEventListener('click', () => openSave(state.mode === 'custom' ? workbench.currentFile() : output.currentFile(), state.outputs[state.mode]?.text))
$('#save-reference').addEventListener('click', () => openSave(reference.currentFile(), $('#reference-text').value,
  { recipe: { version: 1, workflow: 'reference', settings: { language: $('#language').value } }, finishing: { options: {} } }))
$('#save-asr').addEventListener('click', async () => {
  try { await fetchJson('/system/settings', { method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ asr_url: $('#asr-url').value }) }); await refreshAsr() } catch (error) { toast(error.message) }
})
$('#test-asr').addEventListener('click', () => refreshAsr().catch((error) => toast(error.message)))
$('#load-model').addEventListener('click', async () => {
  const button = $('#load-model'); button.disabled = true; button.textContent = 'Loading model…'
  try { await fetchJson('/studio/models/load', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ model: $('#system-model').value }) }) } catch (error) { toast(error.message) }
  finally { button.disabled = false; button.textContent = 'Load model'; refreshStatus().catch(() => {}) }
})
$('#unload-model').addEventListener('click', async () => {
  try { await fetchJson('/studio/models/unload', { method: 'POST' }); await refreshStatus() } catch (error) { toast(error.message) }
})
$('#hero-toggle').addEventListener('click', () => setHeaderCollapsed($('#brand-hero').dataset.collapsed !== 'true'))
document.addEventListener('visibilitychange', () => { if (state.tab === 'system' && !document.hidden) gpu.start(); else gpu.stop() })
document.addEventListener('keydown', (event) => { if ((event.ctrlKey || event.metaKey) && event.key === 'Enter' && ['custom','design','clone'].includes(state.tab)) generate().catch((error) => toast(error.message)) })
window.addEventListener('beforeunload', () => { gpu.stop(); recorder.dispose(); state.controller?.abort(); state.player?.stop().catch(() => {}) })
window.addEventListener('hashchange', () => {
  const tab = location.hash.slice(1)
  if (state.capabilities && ['custom','design','clone','voices','api','system'].includes(tab) && tab !== state.tab) activateTab(tab).catch((error) => toast(error.message))
})

function renderModelPolicy(policy) {
  $('#keep-weights').checked = policy.enabled
  const rows = ['custom', 'design', 'clone'].map(mode => {
    const choice = policy.workflows[mode]
    const row = document.createElement('div'); row.className = 'model-policy-row'
    const label = document.createElement('label'); label.className = 'compact-field'
    const title = document.createElement('span'); title.textContent = names[mode]
    const select = document.createElement('select'); select.id = `policy-model-${mode}`
    selectOptions(select, state.capabilities.models.filter(item => item.mode === mode), choice.model)
    label.append(title, select)
    const keepLabel = document.createElement('label'); keepLabel.className = 'checkbox-field'
    const keep = document.createElement('input'); keep.type = 'checkbox'; keep.id = `policy-keep-${mode}`; keep.checked = choice.keep_loaded
    keep.setAttribute('aria-label', `${names[mode]} always loaded`)
    const text = document.createElement('span'); text.textContent = 'Always loaded'
    keepLabel.append(keep, text); row.append(label, keepLabel)
    return row
  })
  $('#model-policy-rows').replaceChildren(...rows)
}

$('#save-model-policy').addEventListener('click', async () => {
  const button = $('#save-model-policy'); button.disabled = true
  $('#model-policy-status').textContent = 'Applying defaults and loading selected weights…'
  const policy = { enabled: $('#keep-weights').checked, workflows: Object.fromEntries(
    ['custom', 'design', 'clone'].map(mode => [mode, {model: $(`#policy-model-${mode}`).value, keep_loaded: $(`#policy-keep-${mode}`).checked}])) }
  try {
    const settings = await fetchJson('/system/settings', { method: 'PUT', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({model_policy: policy}) })
    renderModelPolicy(settings.model_policy)
    for (const [mode, choice] of Object.entries(settings.model_policy.workflows)) {
      state.capabilities.workflow_defaults[mode].model = choice.model
      delete state.models[mode]
    }
    $('#model-policy-status').textContent = 'Defaults saved. Request-only weights unload after each request.'
    await refreshStatus()
  } catch (error) { $('#model-policy-status').textContent = error.message }
  finally { button.disabled = false }
})

async function initialize() {
  await initializeI18n()
  const [capabilities, settings] = await Promise.all([fetchJson('/studio/capabilities'), fetchJson('/system/settings')])
  state.capabilities = capabilities
  await workbench.initialize()
  for (const [mode, defaults] of Object.entries(capabilities.workflow_defaults)) state.textFeed[mode] = defaults.non_streaming_mode
  $('#clone-method').value = String(capabilities.workflow_defaults.clone.xvec_only)
  for (const id of ['chunk-size', 'chunk-size-slider']) { $('#' + id).min = capabilities.chunk_size.min; $('#' + id).max = capabilities.chunk_size.max }
  updateChunkHelp()
  selectOptions($('#language'), capabilities.languages, 'English')
  selectOptions($('#voice-language'), capabilities.languages, 'English')
  selectOptions($('#speaker'), capabilities.speakers, 'Ryan')
  selectOptions($('#system-model'), capabilities.models)
  renderModelPolicy(settings.model_policy)
  $('#save-model-policy').disabled = false
  $('#asr-url').value = settings.asr_url
  $('#api-example').textContent = `curl ${location.origin}/v1/audio/speech -H 'Content-Type: application/json' -d '{"model":"qwen3-tts","input":"Hello from Qwen Studio.","voice":"Ryan","response_format":"mp3"}' --output speech.mp3`
  let saved = null
  try { saved = JSON.parse(sessionStorage.getItem('qwen3tts-ui-state-v1') || 'null') } catch {}
  setHeaderCollapsed(!!saved?.headerCollapsed, false)
  const views = ['custom','design','clone','voices','api','system']
  const requested = location.hash.slice(1)
  const tab = views.includes(requested) ? requested : views.includes(saved?.tab) ? saved.tab : 'custom'
  await activateTab(tab)
  await Promise.all([refreshStatus(), refreshVoices()])
  $('#generate-button').disabled = false
  setInterval(() => { if (!document.hidden) refreshStatus().catch(() => { $('#runtime-state').textContent = 'Service unavailable' }) }, 2000)
}
initialize().catch((error) => { toast(error.message); $('#global-status').textContent = 'Unable to connect to Studio' })
