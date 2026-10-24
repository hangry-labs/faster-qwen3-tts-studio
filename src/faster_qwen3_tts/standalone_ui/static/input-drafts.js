// Mode ownership follows the VoxCPMTTS workbench. Drafts stay in memory only.
export class InputDrafts {
  constructor({ text = '', ssml = '', serializeMagic, loadMagic }) {
    this.mode = 'magic'
    this.drafts = { text, ssml, 'ssml-h': null }
    this.serializeMagic = serializeMagic
    this.loadMagic = loadMagic
    this.lastMagicSource = null
  }

  switchTo(next, currentText, { syncSsmlH = true } = {}) {
    if (!['magic', 'text', 'ssml', 'ssml-h'].includes(next)) throw new Error('Unknown input mode.')
    const previous = this.mode
    if (next === previous) return previous === 'magic' ? null : currentText
    if (previous !== 'magic') this.drafts[previous] = currentText
    // Validate/import before committing the transition. A failure leaves the
    // current draft, selected button and Magic document intact.
    if (previous === 'ssml-h' && next === 'magic' && syncSsmlH && currentText !== this.lastMagicSource) {
      this.loadMagic(currentText)
      this.lastMagicSource = currentText
    }
    if (next === 'ssml-h' && (previous === 'magic' || this.drafts[next] === null)) {
      this.drafts[next] = this.serializeMagic()
      this.lastMagicSource = this.drafts[next]
    }
    this.mode = next
    return next === 'magic' ? null : this.drafts[next]
  }

  replace(mode, value) {
    if (mode !== 'magic') this.drafts[mode] = value
  }
}
