/** Joins class names, skipping empty values. Classes only ever name a block, element or variant; state is an attribute. */
export function cx(...parts: Array<string | false | null | undefined>): string {
  return parts.filter(Boolean).join(' ')
}
