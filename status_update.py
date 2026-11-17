from pathlib import Path
import re
D=Path(__file__).parent/'dist'
def apply():
 for f in D.rglob('*.html'):
  if f.name.startswith('__'):continue
  s=f.read_text()
  s=re.sub(r'<aside class="quick-update".*?</aside>','<aside class="activity-status" aria-label="Site notifications"><div class="activity-content"><svg class="activity-icon" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M12 11v6m0-10v1"/></svg><span id="activity-message" role="status" aria-live="polite" aria-atomic="true"></span><button type="button" class="activity-dismiss" aria-label="Dismiss notification" tabindex="-1">×</button></div></aside>',s,flags=re.S)
  s=s.replace('<script src="/assets/refined.js" defer></script>','<script src="/assets/refined.js" defer></script><script src="/assets/status.js" defer></script>')
  f.write_text(s)
