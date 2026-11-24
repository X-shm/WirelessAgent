import assert from "node:assert/strict";
import test from "node:test";
import { chatEvents, citationHref, citationLocationLabel, protocolModelKey } from "../assets/protocol-chat.js";

const url = "https://www.etsi.org/deliver/etsi_ts/129500_129599/129512/19.07.00_60/ts_129512v190700p.pdf";
const source = { spec: "3GPP TS 29.512", release: 19, version: "19.7.0", url };

test("reads the current key for the recorded generation endpoint without substituting another provider", () => {
  const baseUrl = "https://fixture.invalid/v1";
  const record = { modelId: "chosen", model: "fixture", baseUrl };
  const configs = [
    { id: "other", model: "fixture", baseUrl, apiKey: "other-key" },
    { id: "chosen", model: "fixture", baseUrl, apiKey: " updated-key " },
  ];
  assert.equal(protocolModelKey(record, configs), "updated-key");
  assert.equal(protocolModelKey({ ...record, modelId: "deleted" }, configs), null);
  assert.equal(protocolModelKey(record, [configs[0]]), "other-key");
  assert.equal(protocolModelKey(record, []), null);
  assert.equal(protocolModelKey({ ...record, baseUrl: "https://elsewhere.invalid/v1" }, configs), null);
});

test("decodes SSE frames across byte boundaries and handles reset and completion", async () => {
  const events = [{ token: "部分回答", seq: 1 }, { reset: true, seq: 2 }, { done: true, answer: "新回答", seq: 3 }];
  const bytes = new TextEncoder().encode(
    ": keepalive\r\n\r\n" + events.map((event) => `data: ${JSON.stringify(event)}`).join("\r\n\r\n"),
  );
  const response = new Response(new ReadableStream({
    start(controller) {
      for (const byte of bytes) controller.enqueue(Uint8Array.of(byte));
      controller.close();
    },
  }));
  const received = [];
  for await (const event of chatEvents(response)) received.push(event);
  assert.deepEqual(received, events);
});

test("only links official PDFs for the supplied specification and version", () => {
  assert.equal(citationHref({ ...source, pdf_page_start: 14 }), url + "#page=14");
  assert.equal(citationHref({ ...source, pdf_page_start: "14" }), url);
  for (const invalid of [
    { version: "17.6.0", release: 17 },
    { spec: "3GPP TS 29.500" },
    { url: url.replace("www.etsi.org", "assets.example.org") },
    { url: url.replace("www.etsi.org", "user@www.etsi.org") },
    { url: url + "#page=91" },
  ]) {
    assert.equal(citationHref({ ...source, ...invalid }), null);
  }
});

test("labels evidence pages, clause fallback, and full PDF separately", () => {
  const exact = { ...source, citation_location: "evidence", pdf_page_start: 33 };
  const clause = { ...source, citation_location: "clause", pdf_page_start: 30 };
  const whole = { ...source, citation_location: "document", pdf_page_start: 90 };
  assert.equal(citationHref(exact), url + "#page=33");
  assert.equal(citationLocationLabel(exact), "PDF 第 33 页");
  assert.equal(citationHref(clause), url + "#page=30");
  assert.equal(citationLocationLabel(clause), "条款起始页（PDF 第 30 页）");
  assert.equal(citationHref(whole), url);
  assert.equal(citationLocationLabel(whole), "同版本 PDF");
});
