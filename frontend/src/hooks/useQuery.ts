import { useState, useCallback } from "react";
import type { QueryResponse } from "../types";
import { submitQuery } from "../api/client";

interface UseQueryState {
  loading: boolean;
  result: QueryResponse | null;
  error: string | null;
}

export function useQuery() {
  const [state, setState] = useState<UseQueryState>({
    loading: false,
    result: null,
    error: null,
  });

  const execute = useCallback(async (query: string) => {
    setState({ loading: true, result: null, error: null });
    try {
      const result = await submitQuery(query);
      if (result.error) {
        setState({ loading: false, result, error: result.error });
      } else {
        setState({ loading: false, result, error: null });
      }
      return result;
    } catch (err) {
      const message = err instanceof Error ? err.message : "An unexpected error occurred";
      setState({ loading: false, result: null, error: message });
      return null;
    }
  }, []);

  const clear = useCallback(() => {
    setState({ loading: false, result: null, error: null });
  }, []);

  return { ...state, execute, clear };
}
