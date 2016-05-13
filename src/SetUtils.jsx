export function union(a, b) {
  return new Set([...a, ...b]);
}

export function intersection(a, b) {
  return new Set([...a].filter(x => b.has(x)));
}

export function difference(a, b) {
  return new Set([...a].filter(x => !b.has(x)));
}
