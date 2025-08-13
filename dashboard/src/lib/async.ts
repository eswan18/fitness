/**
 * Run async tasks over a list with a concurrency limit.
 * Resolves when all tasks complete (successes and failures).
 */
export async function runWithConcurrency<T>(
  items: T[],
  limit: number,
  fn: (item: T, index: number) => Promise<void>,
): Promise<void> {
  let index = 0;
  const workers: Promise<void>[] = [];
  for (let i = 0; i < Math.min(limit, items.length); i++) {
    const worker = (async () => {
      while (true) {
        const current = index++;
        if (current >= items.length) break;
        await fn(items[current], current);
      }
    })();
    workers.push(worker);
  }
  await Promise.all(workers);
}
