def safe_trim_messages(messages, max_len=40):
    """
    Trim messages safely while preserving AI→Tool→AI call/response sequence integrity.
    Works with LangGraph-style dict message objects.
    """
    n = len(messages)
    if n <= max_len:
        return messages

    start = n - max_len

    # Walk backwards to make sure we don't cut inside a tool-call sequence
    while start > 0:
        msg = messages[start]
        msg_type = msg.get("type")
        data = msg.get("data", {})
        tool_calls = data.get("tool_calls", [])

        if msg_type == "ai" and tool_calls:
            start -= 1
            continue

        # If the next message is a tool response, include the AI that triggered it
        if msg_type == "tool":

            found = False
            for j in range(start - 1, -1, -1):
                prev = messages[j]
                prev_data = prev.get("data", {})
                prev_calls = prev_data.get("tool_calls", [])
                if prev.get("type") == "ai" and prev_calls:
                    start = j  # include the whole pair
                    found = True
                    break
            if not found:
                # orphaned tool response → discard it
                start += 1
            continue

        break

    return messages[start:]

# Makes sure: Human -> Ai-ToolRequest -> ToolOutput -> Ai-tool-response sequence integrity
def enforce_sequence(messages, last_msgs=40):
    processed_messages = safe_trim_messages(messages, last_msgs)
    return processed_messages