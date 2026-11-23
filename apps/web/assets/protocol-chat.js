export async function* chatEvents(response) {
  if (!response.ok || !response.body) throw new Error(`Chat request failed (${response.status})`);
  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let pending = "";
  try {
    while (true) {
      const { done, value } = await reader.read();
      pending += decoder.decode(value, { stream: !done });
      const lines = pending.split(/\r?\n/);
      pending = done ? "" : lines.pop();
      for (const line of lines) {
        if (line.startsWith("data: ")) yield JSON.parse(line.slice(6));
      }
      if (done) break;
    }
  } finally {
    await reader.cancel().catch(() => {});
    reader.releaseLock();
  }
}

export function protocolModelKey(record, modelList) {
  if (!record.baseUrl || !Array.isArray(modelList)) return null;
  const matching = modelList.filter((model) => model && model.model === record.model && model.baseUrl === record.baseUrl);
  const chosen = matching.find((model) => model.id === record.modelId) ?? (matching.length === 1 ? matching[0] : null);
  return chosen?.apiKey?.trim() || null;
}

export function citationHref(source) {
  const spec = /^3GPP TS (\d{2})\.(\d{3})$/.exec(source.spec);
  const version = /^(\d{1,2})\.(\d{1,2})\.(\d{1,2})$/.exec(source.version);
  if (!spec || !version || Number(version[1]) !== Number(source.release)) return null;
  try {
    const url = new URL(source.url);
    const number = `1${spec[1]}${spec[2]}`;
    const series = number.slice(0, 4);
    const parts = version.slice(1).map((part) => part.padStart(2, "0"));
    const pattern = new RegExp(`^/deliver/etsi_ts/${series}00_${series}99/${number}/${parts.join("\\.")}_\\d+/ts_${number}v${parts.join("")}p\\.pdf$`);
    if (url.origin !== "https://www.etsi.org" || url.username || url.password || url.search || url.hash || !pattern.test(url.pathname)) return null;
    if (Number.isInteger(source.pdf_page_start) && source.pdf_page_start > 0) url.hash = `page=${source.pdf_page_start}`;
    return url.href;
  } catch {
    return null;
  }
}
