"""
Generate flowchart images for all experiment reports.
Narrow flowcharts use top-to-bottom layout.
Wide/multi-branch flowcharts use left-to-right layout.
"""
from PIL import Image, ImageDraw, ImageFont
import os

# Try to find a suitable Chinese font
FONT_PATHS = [
    "C:/Windows/Fonts/msyh.ttc",     # 微软雅黑
    "C:/Windows/Fonts/simhei.ttf",   # 黑体
    "C:/Windows/Fonts/simsun.ttc",   # 宋体
    "C:/Windows/Fonts/simkai.ttf",   # 楷体
]

FONT_PATH = None
for fp in FONT_PATHS:
    if os.path.exists(fp):
        FONT_PATH = fp
        break

if FONT_PATH is None:
    # Fallback - search fonts directory
    import glob
    fonts = glob.glob("C:/Windows/Fonts/*.tt*")
    FONT_PATH = fonts[0] if fonts else None

FONT_SIZE = 14
FONT_SIZE_SMALL = 12
BOX_PAD_X = 14
BOX_PAD_Y = 8
ARROW_GAP = 6
COLORS = {
    'start_end': ('#4472C4', '#FFFFFF'),   # Blue bg, white text
    'process':   ('#FFFFFF', '#333333'),    # White bg, dark text
    'decision':  ('#ED7D31', '#FFFFFF'),   # Orange bg, white text  
    'io':        ('#70AD47', '#FFFFFF'),   # Green bg, white text
    'line':      '#555555',
    'bg':        '#FAFAFA',
}

def get_font(size):
    try:
        return ImageFont.truetype(FONT_PATH, size)
    except:
        return ImageFont.load_default()

def draw_box(draw, x, y, w, h, box_type='process'):
    """Draw a box and return the text position."""
    bg, fg = COLORS.get(box_type, COLORS['process'])
    if box_type == 'decision':
        # Diamond
        cx, cy = x + w//2, y + h//2
        pts = [(cx, y), (x + w, cy), (cx, y + h), (x, cy)]
        draw.polygon(pts, fill=bg, outline=COLORS['line'], width=2)
    elif box_type in ('start_end',):
        # Rounded rectangle
        r = min(w, h) // 4
        draw.rounded_rectangle([x, y, x+w, y+h], radius=r, fill=bg, outline=COLORS['line'], width=2)
    else:
        draw.rectangle([x, y, x+w, y+h], fill=bg, outline=COLORS['line'], width=2)
    return x + w//2, y + h//2  # center

def draw_arrow_v(draw, x, y1, y2):
    """Draw vertical arrow from y1 to y2."""
    if y2 > y1:
        draw.line([(x, y1), (x, y2 - 10)], fill=COLORS['line'], width=2)
        # arrowhead
        draw.polygon([(x-5, y2-10), (x+5, y2-10), (x, y2)], fill=COLORS['line'])
    else:
        draw.line([(x, y1), (x, y2 + 10)], fill=COLORS['line'], width=2)
        draw.polygon([(x-5, y2+10), (x+5, y2+10), (x, y2)], fill=COLORS['line'])

def draw_arrow_h(draw, y, x1, x2):
    """Draw horizontal arrow from x1 to x2."""
    if x2 > x1:
        draw.line([(x1, y), (x2 - 10, y)], fill=COLORS['line'], width=2)
        draw.polygon([(x2-10, y-5), (x2-10, y+5), (x2, y)], fill=COLORS['line'])
    else:
        draw.line([(x1, y), (x2 + 10, y)], fill=COLORS['line'], width=2)
        draw.polygon([(x2+10, y-5), (x2+10, y+5), (x2, y)], fill=COLORS['line'])

def add_text(draw, cx, cy, text, font, box_type='process'):
    """Add centered text to box."""
    _, fg = COLORS.get(box_type, COLORS['process'])
    lines = text.split('\n')
    line_h = font.size + 4
    total_h = len(lines) * line_h
    start_y = cy - total_h // 2 + 2
    
    for i, line in enumerate(lines):
        bbox = draw.textbbox((0, 0), line, font=font)
        tw = bbox[2] - bbox[0]
        draw.text((cx - tw//2, start_y + i * line_h), line, fill=fg, font=font)

def calc_box_size(text, font):
    """Calculate box width/height for text."""
    lines = text.split('\n')
    max_w = 0
    for line in lines:
        bbox = font.getbbox(line)
        max_w = max(max_w, bbox[2] - bbox[0])
    line_h = font.size + 4
    return max_w + BOX_PAD_X * 2, len(lines) * line_h + BOX_PAD_Y * 2

def make_label(draw, x, y, text, font):
    """Draw a text label at position."""
    draw.text((x, y), text, fill='#555555', font=font)


# ============================================
# Lab3 项目1: 100个数累加 - top-to-bottom
# ============================================
def gen_lab3_proj1():
    font = get_font(FONT_SIZE)
    font_sm = get_font(FONT_SIZE_SMALL)
    
    nodes = [
        ('start_end', '开始'),
        ('process',   'CX=100\nSI→ARRAY\nAX=0'),
        ('process',   'AX=AX+[SI]\nSI=SI+2\nCX=CX-1'),
        ('decision',  'CX=0?'),
        ('process',   'SUM=AX\n程序结束'),
    ]
    
    # Calculate layout
    box_w = 160
    node_heights = []
    for typ, txt in nodes:
        w, h = calc_box_size(txt, font)
        node_heights.append(max(h, 36))
    max_w = max(calc_box_size(t[1], font)[0] for t in nodes)
    box_w = max(max_w + 10, 160)
    
    gap = 30
    img_w = box_w + 80
    img_h = sum(node_heights) + gap * (len(nodes) + 1) + 40
    
    img = Image.new('RGB', (img_w, img_h), COLORS['bg'])
    draw = ImageDraw.Draw(img)
    
    cy = 40
    centers = []
    for i, (typ, txt) in enumerate(nodes):
        h = node_heights[i]
        cx = img_w // 2 - box_w // 2
        draw_box(draw, cx, cy, box_w, h, typ)
        add_text(draw, cx + box_w//2, cy + h//2, txt, font, typ)
        centers.append((cx + box_w//2, cy + h))
        cy += h + gap
    
    # Draw arrows between sequential nodes
    for i in range(len(centers) - 1):
        x = centers[i][0]
        y1 = centers[i][1]
        y2 = centers[i+1][1] - node_heights[i+1]
        draw_arrow_v(draw, x, y1, y2)
    
    # Decision branch labels and return arrow
    # "否" branch loops back
    dec_cx = centers[3][0]
    dec_y = centers[3][1]  # bottom of decision box
    process2_top = centers[3][1]  # same level, need right-side loop back
    
    # Loop back arrow from right side
    right_x = img_w - 20
    loop_top_y = centers[2][1] - node_heights[2]
    
    # Label "否" on the right
    make_label(draw, dec_cx + box_w//2 + 10, dec_y - node_heights[3]//2 - 12, '否', font_sm)
    # Label "是" on the bottom
    make_label(draw, dec_cx - 30, dec_y + 5, '是', font_sm)
    
    # Draw return path on right side
    draw.line([(dec_cx + box_w//2, dec_y - node_heights[3]//2),
                (right_x, dec_y - node_heights[3]//2),
                (right_x, loop_top_y + node_heights[2]//2),
                (dec_cx + box_w//2, loop_top_y + node_heights[2]//2)],
               fill=COLORS['line'], width=2)
    # Arrowhead pointing down
    draw.polygon([(dec_cx + box_w//2 - 5, loop_top_y + node_heights[2]//2 - 8),
                   (dec_cx + box_w//2 + 5, loop_top_y + node_heights[2]//2 - 8),
                   (dec_cx + box_w//2, loop_top_y + node_heights[2]//2)],
                  fill=COLORS['line'])
    
    out_path = 'Lab3/pic/flowchart_proj1.png'
    img.save(out_path)
    print(f'Saved: {out_path}')
    return out_path


# ============================================
# Lab3 项目2: S=1+2×3+... - top-to-bottom
# ============================================
def gen_lab3_proj2():
    font = get_font(FONT_SIZE)
    font_sm = get_font(FONT_SIZE_SMALL)
    
    nodes = [
        ('start_end', '开始\nS=1, N=2'),
        ('process',   'TERM=N×(N+1)'),
        ('decision',  'TERM > 200?'),
        ('process',   'S = S + TERM\nN = N + 1'),
        ('process',   '输出 S 的值\n程序结束'),
    ]
    
    box_w = 170
    node_h_list = []
    for _, txt in nodes:
        _, h = calc_box_size(txt, font)
        node_h_list.append(max(h, 38))
    max_w = max(calc_box_size(t[1], font)[0] for t in nodes)
    box_w = max(max_w + 10, 170)
    
    gap = 28
    img_w = box_w + 120
    img_h = 420
    
    img = Image.new('RGB', (img_w, img_h), COLORS['bg'])
    draw = ImageDraw.Draw(img)
    
    cy = 30
    centers = []
    for i, (typ, txt) in enumerate(nodes):
        h = node_h_list[i]
        cx = img_w // 2 - box_w // 2
        draw_box(draw, cx, cy, box_w, h, typ)
        add_text(draw, cx + box_w//2, cy + h//2, txt, font, typ)
        centers.append((cx + box_w//2, cy + h))
        cy += h + gap
    
    # Straight arrows
    for i in range(3):
        draw_arrow_v(draw, centers[i][0], centers[i][1], centers[i+1][1] - node_h_list[i+1])
    # From end of loop (node 3) back to node 1
    right_x = img_w - 20
    dec_y_mid = centers[1][1] - node_h_list[1]//2
    process_bot = centers[2][1]  # bottom of process 3
    process_top = centers[1][1] - node_h_list[1]  # top of term calc
    
    make_label(draw, centers[1][0] + box_w//2 + 8, dec_y_mid - 10, '否', font_sm)
    make_label(draw, centers[1][0] - 25, centers[1][1] + 5, '是', font_sm)
    
    # Return arrow
    node3_mid_y = (centers[2][1] - node_h_list[2] + centers[2][1]) // 2
    draw.line([(centers[2][0] + box_w//2, node3_mid_y),
                (right_x, node3_mid_y),
                (right_x, process_top + node_h_list[1]//2),
                (centers[1][0] + box_w//2, process_top + node_h_list[1]//2)],
               fill=COLORS['line'], width=2)
    draw.polygon([(centers[1][0] + box_w//2 - 5, process_top + node_h_list[1]//2 - 8),
                   (centers[1][0] + box_w//2 + 5, process_top + node_h_list[1]//2 - 8),
                   (centers[1][0] + box_w//2, process_top + node_h_list[1]//2)],
                  fill=COLORS['line'])
    
    # Arrow from decision (是) to output
    draw_arrow_v(draw, centers[1][0], centers[1][1], centers[3][1] - node_h_list[3])
    
    out_path = 'Lab3/pic/flowchart_proj2.png'
    img.save(out_path)
    print(f'Saved: {out_path}')
    return out_path


# ============================================
# Lab3 项目3: lowercase letter - top-to-bottom
# ============================================
def gen_lab3_proj3():
    font = get_font(FONT_SIZE)
    
    nodes = [
        ('start_end', '开始'),
        ('process',   '提示输入小写字母'),
        ('io',        '键盘读入 → BL'),
        ('process',   '输出 BL-1\n(前导字符)'),
        ('process',   '输出 BL\n(当前字符)'),
        ('process',   '输出 BL+1\n(后续字符)'),
        ('start_end', '程序结束'),
    ]
    
    box_w = 170
    node_h_list = []
    for _, txt in nodes:
        _, h = calc_box_size(txt, font)
        node_h_list.append(max(h, 36))
    
    gap = 22
    img_w = box_w + 80
    img_h = sum(node_h_list) + gap * (len(nodes) + 1) + 20
    
    img = Image.new('RGB', (img_w, img_h), COLORS['bg'])
    draw = ImageDraw.Draw(img)
    
    cy = 30
    centers = []
    for i, (typ, txt) in enumerate(nodes):
        h = node_h_list[i]
        cx = img_w // 2 - box_w // 2
        draw_box(draw, cx, cy, box_w, h, typ)
        add_text(draw, cx + box_w//2, cy + h//2, txt, font, typ)
        centers.append((cx + box_w//2, cy + h))
        cy += h + gap
    
    for i in range(len(centers) - 1):
        draw_arrow_v(draw, centers[i][0], centers[i][1], centers[i+1][1] - node_h_list[i+1])
    
    out_path = 'Lab3/pic/flowchart_proj3.png'
    img.save(out_path)
    print(f'Saved: {out_path}')
    return out_path


# ============================================
# Lab3 项目4: Char classification - LEFT-TO-RIGHT (wide)
# ============================================
def gen_lab3_proj4():
    font = get_font(FONT_SIZE)
    font_sm = get_font(FONT_SIZE_SMALL)
    
    # Layout: Start → Input → series of decisions → actions, arranged horizontally
    box_w = 130
    box_h = 52
    decision_w = 100
    decision_h = 60
    
    img_w = 1100
    img_h = 340
    
    img = Image.new('RGB', (img_w, img_h), COLORS['bg'])
    draw = ImageDraw.Draw(img)
    
    # Row 1: flow row (center y)
    row_y = 60
    action_y = 200  # display/exit actions
    x = 30
    
    # Start node
    draw_box(draw, x, row_y, box_w, box_h, 'start_end')
    add_text(draw, x + box_w//2, row_y + box_h//2, '开始', font, 'start_end')
    x += box_w + 20
    
    # Input node
    draw_box(draw, x, row_y, box_w, box_h, 'io')
    add_text(draw, x + box_w//2, row_y + box_h//2, '键盘读入→BL', font, 'io')
    x += box_w + 20
    
    # Decision 1: BL=0DH?
    d1_x = x
    draw_box(draw, x, row_y, decision_w, decision_h, 'decision')
    add_text(draw, x + decision_w//2, row_y + decision_h//2, 'BL=0DH?\n(回车)', font_sm, 'decision')
    d1_cx = x + decision_w//2
    d1_r = x + decision_w
    x += decision_w + 25
    
    # Decision 2: '1'≤BL≤'9'?
    d2_x = x
    draw_box(draw, x, row_y, decision_w, decision_h, 'decision')
    add_text(draw, x + decision_w//2, row_y + decision_h//2, "'1'≤BL\n≤'9'?", font_sm, 'decision')
    d2_cx = x + decision_w//2
    d2_r = x + decision_w
    x += decision_w + 25
    
    # Decision 3: 'A'≤BL≤'Z'?
    d3_x = x
    draw_box(draw, x, row_y, decision_w, decision_h, 'decision')
    add_text(draw, x + decision_w//2, row_y + decision_h//2, "'A'≤BL\n≤'Z'?", font_sm, 'decision')
    d3_cx = x + decision_w//2
    d3_r = x + decision_w
    x += decision_w + 25
    
    # Decision 4: 'a'≤BL≤'z'?
    d4_x = x
    draw_box(draw, x, row_y, decision_w, decision_h, 'decision')
    add_text(draw, x + decision_w//2, row_y + decision_h//2, "'a'≤BL\n≤'z'?", font_sm, 'decision')
    d4_cx = x + decision_w//2
    d4_r = x + decision_w
    x += decision_w + 30
    
    # Horizontal arrows between decisions
    def h_arrow(x1, x2, y):
        draw_arrow_h(draw, y, x1, x2)
    
    h_arrow(d1_r, d2_x, row_y + decision_h//2)
    h_arrow(d2_r, d3_x, row_y + decision_h//2)
    h_arrow(d3_r, d4_x, row_y + decision_h//2)
    
    # "Yes" branches downward → action boxes
    action_w = 130
    action_h = 40
    
    # D1 Yes → 程序结束
    a1_x = d1_cx - action_w//2
    draw_box(draw, a1_x, action_y, action_w, action_h, 'start_end')
    add_text(draw, a1_x + action_w//2, action_y + action_h//2, '程序结束', font, 'start_end')
    draw_arrow_v(draw, d1_cx, row_y + decision_h, action_y)
    make_label(draw, d1_cx - 18, row_y + decision_h + 6, '是', font_sm)
    
    # D1 No → horizontal flow already shown
    
    # D2 Yes → 显示数字字符
    a2_x = d2_cx - action_w//2
    draw_box(draw, a2_x, action_y, action_w, action_h, 'process')
    add_text(draw, a2_x + action_w//2, action_y + action_h//2, '显示数字字符', font, 'process')
    draw_arrow_v(draw, d2_cx, row_y + decision_h, action_y)
    make_label(draw, d2_cx - 18, row_y + decision_h + 6, '是', font_sm)
    
    # D3 Yes → 显示 'c'
    a3_x = d3_cx - action_w//2
    draw_box(draw, a3_x, action_y, action_w, action_h, 'process')
    add_text(draw, a3_x + action_w//2, action_y + action_h//2, "显示 'c'", font, 'process')
    draw_arrow_v(draw, d3_cx, row_y + decision_h, action_y)
    make_label(draw, d3_cx - 18, row_y + decision_h + 6, '是', font_sm)
    
    # D4 Yes → 显示 'c'
    a4_x = d4_cx - action_w//2
    draw_box(draw, a4_x, action_y, action_w, action_h, 'process')
    add_text(draw, a4_x + action_w//2, action_y + action_h//2, "显示 'c'", font, 'process')
    draw_arrow_v(draw, d4_cx, row_y + decision_h, action_y)
    make_label(draw, d4_cx - 18, row_y + decision_h + 6, '是', font_sm)
    
    # Return arrows from action boxes back to input (except exit)
    # D2, D3, D4 actions return; D1 exits
    return_y = 30
    for ax in [a2_x, a3_x, a4_x]:
        acx = ax + action_w//2
        acy = action_y + action_h
        draw.line([(acx, acy), (acx, acy + 15), (acx, return_y),
                    (d2_x + decision_w//2, return_y)],
                   fill=COLORS['line'], width=1)
    
    # "No" labels for D2, D3, D4
    # Already flow through to next
    
    # "No" for D4 → back to input (no display)
    no_x = d4_r + 10
    draw.line([(d4_r, row_y + decision_h//2), (no_x, row_y + decision_h//2),
                (no_x, return_y),
                (d2_x + decision_w//2, return_y)],
               fill=COLORS['line'], width=1)
    make_label(draw, d4_r + 2, row_y + decision_h//2 - 18, '否', font_sm)
    
    # Arrows from start to input
    start_r = 30 + box_w
    input_x = start_r + 20
    h_arrow(start_r, input_x, row_y + box_h//2)
    
    out_path = 'Lab3/pic/flowchart_proj4.png'
    img.save(out_path)
    print(f'Saved: {out_path}')
    return out_path


# ============================================
# Lab4 项目2: REPNE SCASB - top-to-bottom
# ============================================
def gen_lab4_proj2():
    font = get_font(FONT_SIZE)
    font_sm = get_font(FONT_SIZE_SMALL)
    
    nodes = [
        ('start_end', '开始'),
        ('process',   'DI→BUF\nCX=数据块长度\nAL=KEYWORD\nCLD (DF=0)'),
        ('process',   'REPNE SCASB\n(重复扫描)'),
        ('decision',  'ZF=1?'),
        ('process',   'DI = DI - 1\n(回退到关键字地址)'),
        ('process',   'DI = 0\n(未找到)'),
        ('start_end', '程序结束'),
    ]
    
    box_w = 190
    node_h_list = []
    for _, txt in nodes:
        _, h = calc_box_size(txt, font)
        node_h_list.append(max(h, 40))
    
    gap = 25
    img_w = box_w + 120
    img_h = 520
    
    img = Image.new('RGB', (img_w, img_h), COLORS['bg'])
    draw = ImageDraw.Draw(img)
    
    cy = 25
    centers = []
    xs = []
    for i, (typ, txt) in enumerate(nodes):
        h = node_h_list[i]
        cx = img_w // 2 - box_w // 2
        draw_box(draw, cx, cy, box_w, h, typ)
        add_text(draw, cx + box_w//2, cy + h//2, txt, font, typ)
        centers.append((cx + box_w//2, cy + h))
        xs.append(cx + box_w//2)
        cy += h + gap
    
    # Arrow 0→1→2
    draw_arrow_v(draw, xs[0], centers[0][1], centers[1][1] - node_h_list[1])
    draw_arrow_v(draw, xs[1], centers[1][1], centers[2][1] - node_h_list[2])
    
    # Decision: 是 → DI=DI-1 (node 4); 否 → DI=0 (node 5)
    dec_x = xs[2]
    dec_bot = centers[2][1]
    found_top = centers[3][1] - node_h_list[3]
    notfound_top = centers[4][1] - node_h_list[4]
    
    # "是" branch left
    make_label(draw, dec_x - 40, dec_bot - node_h_list[2]//2 - 10, '是', font_sm)
    draw_arrow_v(draw, dec_x - 70, dec_bot, found_top)
    
    # "否" branch right  
    make_label(draw, dec_x + box_w//2 + 8, dec_bot - node_h_list[2]//2 - 10, '否', font_sm)
    draw_arrow_v(draw, dec_x + 70, dec_bot, notfound_top)
    
    # Both merge to end
    # Found path
    draw_arrow_v(draw, xs[3], centers[3][1], centers[5][1] - node_h_list[5])
    # Not found path
    draw_arrow_v(draw, xs[4], centers[4][1], centers[5][1] - node_h_list[5])
    
    out_path = 'Lab4/pic/flowchart_proj2.png'
    img.save(out_path)
    print(f'Saved: {out_path}')
    return out_path


# ============================================
# Lab4 项目3: String length - top-to-bottom
# ============================================
def gen_lab4_proj3():
    font = get_font(FONT_SIZE)
    font_sm = get_font(FONT_SIZE_SMALL)
    
    nodes = [
        ('start_end', '开始\nCX=0, SI→STRING'),
        ('process',   'AL = [SI]'),
        ('decision',  "AL = '$'?"),
        ('process',   'CX = CX + 1\nSI = SI + 1'),
        ('process',   'LENG = CL\n程序结束'),
    ]
    
    box_w = 170
    node_h_list = []
    for _, txt in nodes:
        _, h = calc_box_size(txt, font)
        node_h_list.append(max(h, 38))
    
    gap = 25
    img_w = box_w + 120
    img_h = 440
    
    img = Image.new('RGB', (img_w, img_h), COLORS['bg'])
    draw = ImageDraw.Draw(img)
    
    cy = 30
    centers = []
    xs = []
    for i, (typ, txt) in enumerate(nodes):
        h = node_h_list[i]
        cx = img_w // 2 - box_w // 2
        draw_box(draw, cx, cy, box_w, h, typ)
        add_text(draw, cx + box_w//2, cy + h//2, txt, font, typ)
        centers.append((cx + box_w//2, cy + h))
        xs.append(cx + box_w//2)
        cy += h + gap
    
    # Start → Read
    draw_arrow_v(draw, xs[0], centers[0][1], centers[1][1] - node_h_list[1])
    
    # Decision
    dec_bot = centers[1][1]
    dec_mid_y = (centers[1][1] - node_h_list[1] + centers[1][1]) // 2
    inc_top = centers[2][1] - node_h_list[2]
    end_top = centers[3][1] - node_h_list[3]
    
    # "否" downward → increment
    make_label(draw, xs[1] - 30, dec_bot - node_h_list[1]//2 - 8, '否', font_sm)
    draw_arrow_v(draw, xs[1], dec_bot, inc_top)
    
    # Loop back from increment to read
    right_x = img_w - 25
    inc_mid_y = (centers[2][1] - node_h_list[2] + centers[2][1]) // 2
    read_mid_y = (centers[1][1] - node_h_list[1] + centers[1][1]) // 2
    draw.line([(xs[2] + box_w//2, inc_mid_y),
                (right_x, inc_mid_y),
                (right_x, read_mid_y - node_h_list[1]//2),
                (xs[1] + box_w//2, read_mid_y - node_h_list[1]//2)],
               fill=COLORS['line'], width=2)
    draw.polygon([(xs[1] + box_w//2 - 5, read_mid_y - node_h_list[1]//2 - 8),
                   (xs[1] + box_w//2 + 5, read_mid_y - node_h_list[1]//2 - 8),
                   (xs[1] + box_w//2, read_mid_y - node_h_list[1]//2)],
                  fill=COLORS['line'])
    
    # "是" → end (right side)
    make_label(draw, xs[1] + box_w//2 + 8, dec_mid_y - 10, '是', font_sm)
    draw.line([(xs[1] + box_w//2, dec_mid_y),
                (right_x, dec_mid_y),
                (right_x, centers[3][1] - node_h_list[3] + node_h_list[3]//2),
                (xs[3], centers[3][1] - node_h_list[3] + node_h_list[3]//2)],
               fill=COLORS['line'], width=2)
    draw.polygon([(xs[3] - 5, centers[3][1] - node_h_list[3] + node_h_list[3]//2 - 8),
                   (xs[3] + 5, centers[3][1] - node_h_list[3] + node_h_list[3]//2 - 8),
                   (xs[3], centers[3][1] - node_h_list[3] + node_h_list[3]//2)],
                  fill=COLORS['line'])
    
    out_path = 'Lab4/pic/flowchart_proj3.png'
    img.save(out_path)
    print(f'Saved: {out_path}')
    return out_path


# ============================================
# Lab5 项目2: Binary to Hex - LEFT-TO-RIGHT (wide, shows subroutines)
# ============================================
def gen_lab5_proj2():
    font = get_font(FONT_SIZE)
    font_sm = get_font(FONT_SIZE_SMALL)
    
    img_w = 1000
    img_h = 380
    
    img = Image.new('RGB', (img_w, img_h), COLORS['bg'])
    draw = ImageDraw.Draw(img)
    
    # Main flow: Start → CX=10→ loop → process → loop → end
    main_y = 50
    x = 25
    box_w = 120
    box_h = 42
    
    # Start
    draw_box(draw, x, main_y, box_w, box_h, 'start_end')
    add_text(draw, x + box_w//2, main_y + box_h//2, '主程序开始', font, 'start_end')
    x += box_w + 15
    
    # Init
    draw_box(draw, x, main_y, box_w, box_h, 'process')
    add_text(draw, x + box_w//2, main_y + box_h//2, 'CX=10\nSI→BUF', font_sm, 'process')
    init_r = x + box_w
    x += box_w + 15
    
    # Loop: AL=[SI]
    loop_start_x = x
    draw_box(draw, x, main_y, box_w, box_h, 'process')
    add_text(draw, x + box_w//2, main_y + box_h//2, 'AL = [SI]', font, 'process')
    loop_mid = x + box_w//2
    x += box_w + 20
    
    # High nibble → HEXASC → DISP
    sub_y = 160
    sub_box_w = 100
    sub_box_h = 36
    
    # HEXASC subroutine box
    hex_x = x
    draw_box(draw, x, sub_y, sub_box_w, sub_box_h, 'io')
    add_text(draw, x + sub_box_w//2, sub_y + sub_box_h//2, 'HEXASC\n子程序', font_sm, 'io')
    
    # Arrow from loop to HEXASC (down)
    draw_arrow_v(draw, loop_mid, main_y + box_h, sub_y)
    make_label(draw, loop_mid - 40, main_y + box_h + 5, '高4位→', font_sm)
    
    x += sub_box_w + 15
    
    # DISP subroutine
    disp_x = x
    draw_box(draw, x, sub_y, sub_box_w, sub_box_h, 'io')
    add_text(draw, x + sub_box_w//2, sub_y + sub_box_h//2, 'DISP\n子程序', font_sm, 'io')
    
    h_arrow_2 = lambda x1, x2, y: draw_arrow_h(draw, y, x1, x2)
    h_arrow_2(hex_x + sub_box_w, disp_x, sub_y + sub_box_h//2)
    
    x += sub_box_w + 25
    
    # Low nibble → HEXASC → DISP
    hex2_x = x
    draw_box(draw, x, sub_y, sub_box_w, sub_box_h, 'io')
    add_text(draw, x + sub_box_w//2, sub_y + sub_box_h//2, 'HEXASC\n子程序', font_sm, 'io')
    make_label(draw, loop_mid + 5, main_y + box_h + 5, '←低4位', font_sm)
    
    from_loop_x = loop_mid
    draw.line([(from_loop_x, main_y + box_h), (from_loop_x, sub_y + sub_box_h//2),
                (hex2_x, sub_y + sub_box_h//2)],
               fill=COLORS['line'], width=1)
    
    x += sub_box_w + 15
    
    disp2_x = x
    draw_box(draw, x, sub_y, sub_box_w, sub_box_h, 'io')
    add_text(draw, x + sub_box_w//2, sub_y + sub_box_h//2, 'DISP\n子程序', font_sm, 'io')
    h_arrow_2(hex2_x + sub_box_w, disp2_x, sub_y + sub_box_h//2)
    
    x = disp2_x + sub_box_w + 20
    
    # LOOP back
    loop_end_x = x
    draw_box(draw, x, main_y, box_w, box_h, 'process')
    add_text(draw, x + box_w//2, main_y + box_h//2, 'SI=SI+1\nCX--, LOOP', font_sm, 'process')
    
    # Arrow from DISP back up
    disp_mid = disp2_x + sub_box_w//2
    draw.line([(disp_mid, sub_y + sub_box_h), (disp_mid, main_y + box_h + 10),
                (loop_end_x + box_w//2, main_y + box_h + 10),
                (loop_end_x + box_w//2, main_y + box_h)],
               fill=COLORS['line'], width=1)
    
    x += box_w + 20
    
    # End
    draw_box(draw, x, main_y, box_w, box_h, 'start_end')
    add_text(draw, x + box_w//2, main_y + box_h//2, '程序结束', font, 'start_end')
    
    # Arrows along main path
    h_arrow_2(30 + box_w, 45, main_y + box_h//2)  # start→init
    h_arrow_2(init_r, loop_start_x, main_y + box_h//2)  # init→loop
    h_arrow_2(loop_start_x + box_w, hex_x, main_y + box_h//2)  # loop→hex
    h_arrow_2(loop_end_x + box_w, x, main_y + box_h//2)  # loop end→end
    
    # Loop back arrow from LOOP node to AL=[SI]
    return_y = 20
    loop_bot = main_y + box_h
    draw.line([(loop_end_x + box_w//2, loop_bot), (loop_end_x + box_w//2, loop_bot + 20),
                (loop_start_x + box_w//2, loop_bot + 20),
                (loop_start_x + box_w//2, loop_bot)],
               fill=COLORS['line'], width=2)
    draw.polygon([(loop_start_x + box_w//2 - 5, loop_bot - 8),
                   (loop_start_x + box_w//2 + 5, loop_bot - 8),
                   (loop_start_x + box_w//2, loop_bot)],
                  fill=COLORS['line'])
    make_label(draw, (loop_end_x + loop_start_x)//2 + 20, loop_bot + 6, 'CX≠0', font_sm)
    
    out_path = 'Lab5/pic/flowchart_proj2.png'
    img.save(out_path)
    print(f'Saved: {out_path}')
    return out_path


# ============================================
# Lab6 项目2: Bell ring - top-to-bottom
# ============================================
def gen_lab6_proj2():
    font = get_font(FONT_SIZE)
    font_sm = get_font(FONT_SIZE_SMALL)
    
    nodes = [
        ('start_end', '开始'),
        ('process',   '显示提示信息'),
        ('io',        '键盘输入字符\nAL = ASCII码'),
        ('process',   'ASCII→数字\nSUB AL,30H\nCX = AX'),
        ('decision',  'CX = 0?'),
        ('process',   '响铃一次 (07H)\n延时等待\nCX = CX - 1'),
        ('start_end', '程序结束'),
    ]
    
    box_w = 170
    node_h_list = []
    for _, txt in nodes:
        _, h = calc_box_size(txt, font)
        node_h_list.append(max(h, 40))
    
    gap = 22
    img_w = box_w + 120
    img_h = 500
    
    img = Image.new('RGB', (img_w, img_h), COLORS['bg'])
    draw = ImageDraw.Draw(img)
    
    cy = 25
    centers = []
    xs = []
    for i, (typ, txt) in enumerate(nodes):
        h = node_h_list[i]
        cx = img_w // 2 - box_w // 2
        draw_box(draw, cx, cy, box_w, h, typ)
        add_text(draw, cx + box_w//2, cy + h//2, txt, font, typ)
        centers.append((cx + box_w//2, cy + h))
        xs.append(cx + box_w//2)
        cy += h + gap
    
    # Straight arrows 0→1→2→3
    for i in range(3):
        draw_arrow_v(draw, xs[i], centers[i][1], centers[i+1][1] - node_h_list[i+1])
    
    # Decision: "否" → ring + loop back; "是" → end
    dec_x = xs[3]
    dec_bot = centers[3][1]
    ring_top = centers[4][1] - node_h_list[4]
    end_top = centers[5][1] - node_h_list[5]
    
    make_label(draw, dec_x - 30, dec_bot - node_h_list[3]//2 - 8, '否', font_sm)
    draw_arrow_v(draw, dec_x, dec_bot, ring_top)
    
    # Loop back from ring to decision
    right_x = img_w - 25
    ring_mid_y = (centers[4][1] - node_h_list[4] + centers[4][1]) // 2
    dec_mid_y = (centers[3][1] - node_h_list[3] + centers[3][1]) // 2
    draw.line([(xs[4] + box_w//2, ring_mid_y),
                (right_x, ring_mid_y),
                (right_x, dec_mid_y),
                (xs[3] + box_w//2, dec_mid_y)],
               fill=COLORS['line'], width=2)
    draw.polygon([(xs[3] + box_w//2 - 5, dec_mid_y - 8),
                   (xs[3] + box_w//2 + 5, dec_mid_y - 8),
                   (xs[3] + box_w//2, dec_mid_y)],
                  fill=COLORS['line'])
    
    # "是" → end
    make_label(draw, dec_x + box_w//2 + 8, dec_mid_y - 10, '是', font_sm)
    draw.line([(xs[3] + box_w//2, dec_mid_y + 5),
                (right_x + 40, dec_mid_y + 5),
                (right_x + 40, centers[5][1] - node_h_list[5] + node_h_list[5]//2),
                (xs[5], centers[5][1] - node_h_list[5] + node_h_list[5]//2)],
               fill=COLORS['line'], width=2)
    draw.polygon([(xs[5] - 5, centers[5][1] - node_h_list[5] + node_h_list[5]//2 - 8),
                   (xs[5] + 5, centers[5][1] - node_h_list[5] + node_h_list[5]//2 - 8),
                   (xs[5], centers[5][1] - node_h_list[5] + node_h_list[5]//2)],
                  fill=COLORS['line'])
    
    out_path = 'Lab6/pic/flowchart_proj2.png'
    img.save(out_path)
    print(f'Saved: {out_path}')
    return out_path


# ============================================
# Lab6 项目3: Grade statistics - LEFT-TO-RIGHT (wide, multi-branch)
# ============================================
def gen_lab6_proj3():
    font = get_font(FONT_SIZE)
    font_sm = get_font(FONT_SIZE_SMALL)
    
    img_w = 1150
    img_h = 400
    
    img = Image.new('RGB', (img_w, img_h), COLORS['bg'])
    draw = ImageDraw.Draw(img)
    
    # Top row: flow of decisions
    flow_y = 40
    x = 20
    box_w = 110
    box_h = 42
    dec_w = 95
    dec_h = 56
    
    # Start
    draw_box(draw, x, flow_y, box_w, box_h, 'start_end')
    add_text(draw, x + box_w//2, flow_y + box_h//2, '开始', font, 'start_end')
    x += box_w + 5
    
    # Init
    draw_box(draw, x, flow_y, box_w, box_h, 'process')
    add_text(draw, x + box_w//2, flow_y + box_h//2, '初始化计数器\nS6~S10=0', font_sm, 'process')
    init_r = x + box_w
    x += box_w + 5
    
    # CX=10, SI→scores
    draw_box(draw, x, flow_y, box_w, box_h, 'process')
    add_text(draw, x + box_w//2, flow_y + box_h//2, 'CX=10\nSI→SCORES', font_sm, 'process')
    init2_r = x + box_w
    x += box_w + 8
    
    # Loop: AL=[SI]
    loop_x = x
    draw_box(draw, x, flow_y, box_w, box_h, 'process')
    add_text(draw, x + box_w//2, flow_y + box_h//2, 'AL = [SI]', font, 'process')
    loop_r = x + box_w
    x += box_w + 8
    
    # Decision chain: =100?, ≥90?, ≥80?, ≥70?, ≥60?
    decisions = [
        ('AL=100?', 'S10++'),
        ('AL≥90?', 'S9++'),
        ('AL≥80?', 'S8++'),
        ('AL≥70?', 'S7++'),
        ('AL≥60?', 'S6++'),
    ]
    
    dec_info = []
    for label, action in decisions:
        d_x = x
        draw_box(draw, x, flow_y, dec_w, dec_h, 'decision')
        add_text(draw, x + dec_w//2, flow_y + dec_h//2, label, font_sm, 'decision')
        dec_info.append((x + dec_w//2, x + dec_w, label, action))
        x += dec_w + 5
    
    last_dec_r = x - 5
    
    # NEXT_SCORE box
    next_x = x
    next_w = 115
    draw_box(draw, x, flow_y, next_w, box_h, 'process')
    add_text(draw, x + next_w//2, flow_y + box_h//2, 'NEXT_SCORE\nSI++, LOOP', font_sm, 'process')
    next_r = x + next_w
    x += next_w + 10
    
    # End box
    draw_box(draw, x, flow_y, box_w, box_h, 'start_end')
    add_text(draw, x + box_w//2, flow_y + box_h//2, '显示统计结果\n程序结束', font_sm, 'start_end')
    end_x = x
    end_r = x + box_w
    
    # Horizontal arrows along flow
    def h_arr(x1, x2, y):
        draw_arrow_h(draw, y, x1, x2)
    
    h_arr(20 + box_w, 40, flow_y + box_h//2)
    h_arr(init_r, 50, flow_y + box_h//2)
    h_arr(init2_r, loop_x, flow_y + box_h//2)
    h_arr(loop_r, dec_info[0][0] - dec_w//2, flow_y + dec_h//2)
    
    for i in range(len(dec_info) - 1):
        h_arr(dec_info[i][1], dec_info[i+1][0] - dec_w//2, flow_y + dec_h//2)
    
    h_arr(last_dec_r, next_x, flow_y + box_h//2)
    h_arr(next_r, end_x, flow_y + box_h//2)
    
    # "Yes" branches downward → action boxes
    action_y = 200
    act_w = 90
    act_h = 36
    
    for i, (dcx, d_r, label, action) in enumerate(dec_info):
        ax = dcx - act_w//2
        draw_box(draw, ax, action_y, act_w, act_h, 'process')
        add_text(draw, ax + act_w//2, action_y + act_h//2, action, font_sm, 'process')
        draw_arrow_v(draw, dcx, flow_y + dec_h, action_y)
        make_label(draw, dcx - 12, flow_y + dec_h + 6, '是', font_sm)
        
        # Arrow from action to NEXT_SCORE
        # Each action feeds into NEXT_SCORE
        if i < len(dec_info) - 1:
            # Route down and to next
            action_bot = action_y + act_h
            next_mid = next_x + next_w//2
            draw.line([(dcx, action_bot), (dcx, action_bot + 10),
                        (next_mid, action_bot + 10), (next_mid, action_y)],
                       fill=COLORS['line'], width=1)
    
    # Last decision's action also routes to NEXT_SCORE
    last_dcx = dec_info[-1][0]
    action_bot = action_y + act_h
    next_mid = next_x + next_w//2
    draw.line([(last_dcx, action_bot), (last_dcx, action_bot + 10),
                (next_mid, action_bot + 10), (next_mid, action_y)],
               fill=COLORS['line'], width=1)
    
    # "No" paths skip to next
    for i, (dcx, d_r, _, _) in enumerate(dec_info):
        make_label(draw, d_r + 1, flow_y + dec_h//2 - 18, '否', font_sm)
    
    # Loop back from NEXT_SCORE to loop start
    loop_bot = flow_y + box_h
    return_y = flow_y - 15
    draw.line([(next_mid, loop_bot), (next_mid, loop_bot + 15),
                (loop_x + box_w//2, loop_bot + 15), (loop_x + box_w//2, loop_bot)],
               fill=COLORS['line'], width=2)
    draw.polygon([(loop_x + box_w//2 - 5, loop_bot - 8),
                   (loop_x + box_w//2 + 5, loop_bot - 8),
                   (loop_x + box_w//2, loop_bot)],
                  fill=COLORS['line'])
    make_label(draw, (next_mid + loop_x + box_w//2)//2 - 15, loop_bot + 7, 'CX≠0', font_sm)
    
    out_path = 'Lab6/pic/flowchart_proj3.png'
    img.save(out_path)
    print(f'Saved: {out_path}')
    return out_path


# ============================================
# Generate all
# ============================================
if __name__ == '__main__':
    print(f'Using font: {FONT_PATH}')
    gen_lab3_proj1()
    gen_lab3_proj2()
    gen_lab3_proj3()
    gen_lab3_proj4()
    gen_lab4_proj2()
    gen_lab4_proj3()
    gen_lab5_proj2()
    gen_lab6_proj2()
    gen_lab6_proj3()
    print('\nAll flowcharts generated!')
