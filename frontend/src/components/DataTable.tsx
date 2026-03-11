import { useState, useMemo } from "react";

interface DataTableProps {
  columns: string[];
  rows: (string | number | boolean | null)[][];
}

type SortDir = "asc" | "desc" | null;

export default function DataTable({ columns, rows }: DataTableProps) {
  const [sortCol, setSortCol] = useState<number | null>(null);
  const [sortDir, setSortDir] = useState<SortDir>(null);

  const handleSort = (colIdx: number) => {
    if (sortCol === colIdx) {
      if (sortDir === "asc") setSortDir("desc");
      else if (sortDir === "desc") {
        setSortCol(null);
        setSortDir(null);
      }
    } else {
      setSortCol(colIdx);
      setSortDir("asc");
    }
  };

  const sortedRows = useMemo(() => {
    if (sortCol === null || sortDir === null) return rows;
    return [...rows].sort((a, b) => {
      const aVal = a[sortCol];
      const bVal = b[sortCol];
      if (aVal === null && bVal === null) return 0;
      if (aVal === null) return 1;
      if (bVal === null) return -1;
      if (typeof aVal === "number" && typeof bVal === "number") {
        return sortDir === "asc" ? aVal - bVal : bVal - aVal;
      }
      const aStr = String(aVal);
      const bStr = String(bVal);
      return sortDir === "asc" ? aStr.localeCompare(bStr) : bStr.localeCompare(aStr);
    });
  }, [rows, sortCol, sortDir]);

  const sortIndicator = (colIdx: number) => {
    if (sortCol !== colIdx) return " ";
    return sortDir === "asc" ? " \u2191" : " \u2193";
  };

  return (
    <div className="space-y-2">
      <div className="text-xs text-dark-muted">
        {rows.length} row{rows.length !== 1 ? "s" : ""}
      </div>
      <div className="overflow-auto rounded-lg border border-dark-border max-h-96">
        <table className="w-full text-sm">
          <thead className="sticky top-0 z-10">
            <tr className="bg-dark-surface border-b border-dark-border">
              {columns.map((col, i) => (
                <th
                  key={i}
                  onClick={() => handleSort(i)}
                  className="px-4 py-2.5 text-left text-xs font-semibold text-dark-muted uppercase tracking-wide cursor-pointer hover:text-accent select-none whitespace-nowrap"
                >
                  {col}
                  <span className="text-accent">{sortIndicator(i)}</span>
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {sortedRows.map((row, rIdx) => (
              <tr
                key={rIdx}
                className={`border-b border-dark-border last:border-b-0 ${
                  rIdx % 2 === 0 ? "bg-dark-bg" : "bg-dark-surface/50"
                }`}
              >
                {row.map((cell, cIdx) => (
                  <td key={cIdx} className="px-4 py-2 text-dark-text whitespace-nowrap">
                    {cell === null ? (
                      <span className="text-dark-muted italic">null</span>
                    ) : (
                      String(cell)
                    )}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
