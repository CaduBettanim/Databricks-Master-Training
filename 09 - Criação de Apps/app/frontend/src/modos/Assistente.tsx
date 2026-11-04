// Aba 2 — Assistente. Chat com o Supervisor em código do app (server/supervisor.py), que escolhe
// entre os Genies de Faturamento e Suporte do Ex.07, via /api/assistente/perguntar.
import { useEffect, useRef, useState } from "react";
import { api, Consulta } from "../api";

type Msg = { de: "u" | "a"; texto: string; who?: string; consultas?: Consulta[] };

export function Assistente() {
  const [msgs, setMsgs] = useState<Msg[]>([
    { de: "a", who: "Supervisor", texto: "Posso ajudar com dúvidas sobre faturamento e suporte dos clientes. O que você quer saber?" },
  ]);
  const [input, setInput] = useState("");
  const [carregando, setCarregando] = useState(false);
  const fimRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    fimRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [msgs, carregando]);

  async function enviar() {
    const v = input.trim();
    if (!v || carregando) return;
    setMsgs((m) => [...m, { de: "u", texto: v }]);
    setInput("");
    setCarregando(true);
    try {
      const r = await api.perguntar(v);
      const rota = r.rota?.length ? ` · via ${r.rota.join(" + ")}` : "";
      setMsgs((m) => [...m, { de: "a", who: `Supervisor${rota}`, texto: r.resposta, consultas: r.consultas }]);
    } catch (e) {
      setMsgs((m) => [...m, { de: "a", who: "Supervisor", texto: "Falha ao consultar o Supervisor. Tente novamente." }]);
    } finally {
      setCarregando(false);
    }
  }

  return (
    <div className="panel">
      <div className="chat" style={{ marginBottom: 12 }}>
        <div className="hd">
          <span className="dot" /> <b>Supervisor</b> &nbsp;·&nbsp; agente em código do app &nbsp;·&nbsp;
          roteia entre os seus Genies <span className="tag">Faturamento</span> e <span className="tag">Suporte</span> (Ex.07)
        </div>
        <div className="msgs">
          {msgs.map((m, i) => (
            <div className={`msg ${m.de}`} key={i}>
              {m.who && <div className="who">{m.who}</div>}
              {m.texto}
              {m.consultas?.map((c, j) => (
                <details className="consulta" key={j}>
                  <summary>
                    <span className="tag">{c.especialista}</span> {c.ok ? "consultado" : "falhou"}
                    {c.ok && c.linhas ? ` · ${c.linhas} linha(s)` : ""}
                  </summary>
                  <div className="muted">Pergunta enviada ao Genie: {c.pergunta}</div>
                  {c.sql && <pre>{c.sql}</pre>}
                </details>
              ))}
            </div>
          ))}
          {carregando && (
            <div className="msg a">
              <div className="who">Supervisor · roteando…</div>
              <span className="spin" /> &nbsp;escolhendo o especialista e consultando o Genie (Faturamento / Suporte)…
            </div>
          )}
          <div ref={fimRef} />
        </div>
        <div className="in">
          <input
            value={input}
            placeholder="Pergunte algo (ex.: NPS médio por canal, faturas em aberto)…"
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && enviar()}
            disabled={carregando}
          />
          <button className="btn btn-primary" onClick={enviar} disabled={carregando}>Enviar</button>
        </div>
      </div>
      <p className="muted" style={{ fontSize: 12 }}>
        Cada pergunta passa pelo Supervisor em código do app (<code>server/supervisor.py</code>): o seu model
        service do Unity Gateway escolhe o especialista, e cada especialista é um Genie Agent que você criou no Ex.07.
      </p>
    </div>
  );
}
