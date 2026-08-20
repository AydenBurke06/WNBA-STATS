"use client";

import { useState } from "react";

type Row = {
  team_id: string;
  games_sampled: number;
  pts_allowed: number;
  reb_allowed: number;
  ast_allowed: number;
  stl_allowed: number;
  blk_allowed: number;
  fg3m_allowed: number;
  fg_pct_allowed: number;
};

type DvpData = { G: Row[]; F: Row[]; C: Row[] };

const POSITIONS = [
  { key: "G", label: "Guards" },
  { key: "F", label: "Forwards" },
  { key: "C", label: "Centers" },
] as const;

export default function DvpTable({ data }: { data: DvpData }) {
  const [position, setPosition] = useState<"G" | "F" | "C">("G");
  const rows = data[position];

  return (
    <>
      <nav className="pill-nav">
        {POSITIONS.map((p) => (
          <button
            key={p.key}
            className={position === p.key ? "active" : ""}
            onClick={() => setPosition(p.key)}
          >
            {p.label}
          </button>
        ))}
      </nav>

      <div className="table-wrap" key={position}>
        {rows.length === 0 ? (
          <p className="state">No data yet — run sync.py and push data/dvp.json.</p>
        ) : (
          <table>
            <thead>
              <tr>
                <th className="rank">#</th>
                <th>Team</th>
                <th className="num">PTS</th>
                <th className="num">REB</th>
                <th className="num">AST</th>
                <th className="num">STL</th>
                <th className="num">BLK</th>
                <th className="num">3PM</th>
                <th className="num">FG%</th>
                <th className="num">GP</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((r, i) => (
                <tr key={r.team_id}>
                  <td className="rank">{i + 1}</td>
                  <td className="team">{r.team_id}</td>
                  <td className="num">{r.pts_allowed}</td>
                  <td className="num">{r.reb_allowed}</td>
                  <td className="num">{r.ast_allowed}</td>
                  <td className="num">{r.stl_allowed}</td>
                  <td className="num">{r.blk_allowed}</td>
                  <td className="num">{r.fg3m_allowed}</td>
                  <td className="num">{r.fg_pct_allowed}</td>
                  <td className="num">{r.games_sampled}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </>
  );
}
