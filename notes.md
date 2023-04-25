## Chart prompt

```python
def answer_to_chart(question: str, results: str) -> str:
    # write a prompt to generate a chart, execute it and save the results
    # to a file with a random filename
    prompt = f"""Given this question:

{question}

and these results:

{results}

write some Python code with matplotlib.pyplot to create a chart 
which illustrates this data.

Only return the Python code. Don't explain your work."""
```
