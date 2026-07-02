import { useEffect, useState } from "react";

interface AsyncState<TData> {
  data: TData | null;
  error: string | null;
  loading: boolean;
}

export function useAsyncData<TData>(
  loader: () => Promise<TData>,
  dependencies: unknown[] = [],
): AsyncState<TData> {
  const [state, setState] = useState<AsyncState<TData>>({
    data: null,
    error: null,
    loading: true,
  });

  useEffect(() => {
    let alive = true;
    setState((current) => ({ ...current, error: null, loading: true }));

    loader()
      .then((data) => {
        if (alive) {
          setState({ data, error: null, loading: false });
        }
      })
      .catch((error: Error) => {
        if (alive) {
          setState({ data: null, error: error.message, loading: false });
        }
      });

    return () => {
      alive = false;
    };
  }, dependencies);

  return state;
}
