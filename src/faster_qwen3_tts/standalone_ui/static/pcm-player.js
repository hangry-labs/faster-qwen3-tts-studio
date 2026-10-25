import { msg } from './i18n.js'
// PCM-WAV chunk playback for the Qwen engine; no MP3 codec or CDN dependency.
export function decodePcmWav(bytes) {
  const view = new DataView(bytes.buffer, bytes.byteOffset, bytes.byteLength)
  let rate = 24000, channels = 1, bits = 16
  for (let offset = 12; offset + 8 <= view.byteLength;) {
    const name = String.fromCharCode(...bytes.slice(offset, offset + 4))
    const size = view.getUint32(offset + 4, true)
    const start = offset + 8
    if (name === 'fmt ') {
      channels = view.getUint16(start + 2, true)
      rate = view.getUint32(start + 4, true)
      bits = view.getUint16(start + 14, true)
    }
    if (name === 'data') {
      if (channels !== 1 || bits !== 16 || start + size > view.byteLength) throw new Error(msg('Unexpected audio chunk format.'))
      const samples = new Float32Array(size / 2)
      for (let index = 0; index < samples.length; index++) samples[index] = view.getInt16(start + index * 2, true) / 32768
      return { samples, rate }
    }
    offset = start + size + (size % 2)
  }
  throw new Error(msg('The audio chunk has no samples.'))
}

export class PcmPlayer {
  constructor() { this.context = new AudioContext(); this.sources = new Set(); this.nextTime = 0 }
  async resume() { await this.context.resume() }
  play(samples, rate) {
    const buffer = this.context.createBuffer(1, samples.length, rate)
    buffer.copyToChannel(samples, 0)
    const source = this.context.createBufferSource()
    source.buffer = buffer
    source.connect(this.context.destination)
    source.addEventListener('ended', () => this.sources.delete(source), { once: true })
    this.sources.add(source)
    this.nextTime = Math.max(this.nextTime, this.context.currentTime + 0.025)
    const scheduledMs = performance.now() + (this.nextTime - this.context.currentTime) * 1000
    source.start(this.nextTime)
    this.nextTime += buffer.duration
    return scheduledMs
  }
  bufferedSeconds() { return this.context.state === 'closed' ? 0 : Math.max(0, this.nextTime - this.context.currentTime) }
  async finish() {
    if (this.context.state === 'closed') return
    const remaining = Math.max(0, this.nextTime - this.context.currentTime)
    await new Promise((resolve) => {
      this.finishResolve = resolve
      this.finishTimer = setTimeout(resolve, remaining * 1000)
    })
    await this.stop()
  }
  async stop() {
    clearTimeout(this.finishTimer)
    this.finishResolve?.()
    this.finishResolve = null
    for (const source of this.sources) { try { source.stop() } catch {} }
    this.sources.clear()
    if (this.context.state !== 'closed') await this.context.close()
  }
}
