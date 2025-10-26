"""
清理工具模块

提供 Gemini CLI 输出清理功能。
"""


def clean_gemini_output(output: str) -> str:
    """
    清理 Gemini CLI 输出的简单启发式方法
    
    Args:
        output: 原始 Gemini CLI 输出
    
    Returns:
        str: 清理后的输出
    """
    if not output:
        return ""
    
    lines = [ln.strip() for ln in output.splitlines()]
    lines = [ln for ln in lines if ln]
    
    cleaned = []
    for ln in lines:
        # 跳过仅包含装饰字符的行
        if set(ln) <= set("-_=*~ ") and len(ln) > 3:
            continue
        # 跳过包含框线字符的行
        if any(c in ln for c in '█░╭╮╯╰│─┌┐└┘'):
            continue
        cleaned.append(ln)
    
    return ' '.join(cleaned).strip()