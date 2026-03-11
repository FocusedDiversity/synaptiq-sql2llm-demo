import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import Header from "../components/Header";
import ErrorDisplay from "../components/ErrorDisplay";
import LoadingSpinner from "../components/LoadingSpinner";
import InsightPanel from "../components/InsightPanel";
import DataTable from "../components/DataTable";

describe("Header", () => {
  it("renders the app title", () => {
    render(<Header />);
    expect(screen.getByText(/SQL2LLM/i)).toBeInTheDocument();
  });
});

describe("ErrorDisplay", () => {
  it("renders error message", () => {
    render(<ErrorDisplay message="Something went wrong" />);
    expect(screen.getByText(/Something went wrong/)).toBeInTheDocument();
  });
});

describe("LoadingSpinner", () => {
  it("renders without crashing", () => {
    const { container } = render(<LoadingSpinner />);
    expect(container.firstChild).toBeTruthy();
  });
});

describe("InsightPanel", () => {
  it("renders insight text", () => {
    render(<InsightPanel insight="Revenue is up 15% this quarter" />);
    expect(screen.getByText(/Revenue is up 15%/)).toBeInTheDocument();
  });
});

describe("DataTable", () => {
  it("renders columns and rows", () => {
    const columns = ["Name", "Age"];
    const rows = [
      ["Alice", 30],
      ["Bob", 25],
    ];
    render(<DataTable columns={columns} rows={rows} />);
    expect(screen.getByText("Name")).toBeInTheDocument();
    expect(screen.getByText("Alice")).toBeInTheDocument();
    expect(screen.getByText("25")).toBeInTheDocument();
  });
});
