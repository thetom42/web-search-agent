# Markdown Formatting Rules

## Lists

1. Always surround lists with blank lines

   ~~~markdown
   Some text here.

   - List item 1
   - List item 2

   More text here.
   ~~~

1. This applies to both ordered and unordered lists

   ~~~markdown
   Previous paragraph.

   1. First item
   1. Second item

   Next paragraph.
   ~~~

## Code Blocks

1. Always surround code fences (``` blocks) with blank lines

   ~~~markdown
   Some text.

   ```python
   def example():
       pass
   ```

   More text.
   ~~~

## Ordered Lists

1. Always use "1." for every item in ordered lists

   ~~~markdown
   1. First item    # Correct
   1. Second item   # Correct
   1. Third item    # Correct

   1. First item    # Correct
   2. Second item   # Wrong
   3. Third item    # Wrong
   ~~~

## Nested Content

1. When a list item contains code blocks or sub-lists, maintain proper indentation and spacing

   ~~~markdown
   1. First item

      ```python
      def example():
          pass
      ```

   1. Second item

      - Sub item 1
      - Sub item 2

   1. Third item
   ~~~

## Common Mistakes to Avoid

1. Missing blank lines around lists

   ~~~markdown
   Some text
   - Item 1    # Wrong
   - Item 2
   More text

   Some text

   - Item 1    # Correct
   - Item 2

   More text
   ~~~

1. Missing blank lines around code fences

   ~~~markdown
   Some text
   ```code
   example
   ```    # Wrong
   More text

   Some text

   ```code
   example
   ```

   More text    # Correct
   ~~~

1. Inconsistent ordered list numbering

   ~~~markdown
   1. First     # Wrong
   2. Second
   3. Third

   1. First     # Correct
   1. Second
   1. Third
   ~~~

## File Formatting

1. Always end files with a newline

   ~~~markdown
   Last line of content
   ⏎             # Correct - File ends with newline

   Last line of content[NO NEWLINE]    # Wrong - No newline at end
   ~~~

## Benefits of Proper Formatting

1. Improved readability

1. Consistent rendering across different markdown processors

1. Easier maintenance and updates

1. Better version control diffs

1. Compliance with common markdown linting tools
