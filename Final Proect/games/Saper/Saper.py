from tkinter import *
from tkinter import messagebox
from random import choice
import time

def open_adjacent(n):
    """Функция рекурсивно открывает соседние клетки, если они пустые (0)."""
    queue = [n]
    visited = set()
    
    while queue:
        cell = queue.pop()
        if cell in visited:
            continue
        visited.add(cell)
        
        btn[cell].config(text=playArea[cell], state=DISABLED, bg='white')
        if playArea[cell] == 0:
            btn[cell].config(text=' ', bg='#ccb')
            neighbors = get_neighbors(cell)
            queue.extend(neighbors)

def get_neighbors(n):
    """Возвращает список соседних индексов для клетки n."""
    neighbors = []
    row, col = divmod(n, xBtn)
    
    for dr, dc in [(-1, -1), (-1, 0), (-1, 1),
                   (0, -1),         (0, 1),
                   (1, -1), (1, 0), (1, 1)]:
        nr, nc = row + dr, col + dc
        if 0 <= nr < yBtn and 0 <= nc < xBtn:
            neighbors.append(nr * xBtn + nc)
    
    return neighbors

def play(n):
    global xBtn, yBtn, mines, nMoves, mrk, playTime
    if len(playArea) < xBtn * yBtn:
        return
    if btn[n].cget('text') == imgMark:  # Не открывать, если стоит флаг
        return

    nMoves += 1
    if nMoves == 1:
        playTime = time.time()
        i = 0
        while i < mines:
            j = choice(range(0, xBtn * yBtn))
            if j != n and playArea[j] != -1:
                playArea[j] = -1
                i += 1
        for i in range(0, xBtn * yBtn):
            if playArea[i] != -1:
                playArea[i] = sum(playArea[neigh] == -1 for neigh in get_neighbors(i))
    
    if playArea[n] == -1:  # Если нажали на мину — показать все мины
        btn[n].config(text=imgMine, bg='red')
        show_all_mines()
        tk.after(1500, game_over)  # 1.5 сек задержка, затем вопрос о перезапуске
        return

    btn[n].config(text=playArea[n], state=DISABLED, bg='white')
    
    if playArea[n] == 0:
        btn[n].config(text=' ', bg='#ccb')
        open_adjacent(n)

def mark_cell(n):
    """Ставит или убирает флажок при правом клике."""
    if btn[n]['state'] == DISABLED:  # Если клетка уже открыта — игнорируем
        return
    current_text = btn[n].cget('text')
    if current_text == ' ':  # Если пустая, ставим флаг
        btn[n].config(text=imgMark, fg='red')
    elif current_text == imgMark:  # Если уже есть флаг, убираем
        btn[n].config(text=' ', fg='black')

def show_all_mines():
    """Открывает все мины на поле."""
    for i in range(xBtn * yBtn):
        if playArea[i] == -1:
            btn[i].config(text=imgMine, bg='gray')

def game_over():
    """Показывает сообщение о проигрыше и предлагает начать заново."""
    if messagebox.askyesno("Игра окончена", "Вы проиграли! Начать заново?"):
        newGame()

def newGame():
    """Перезапуск игры."""
    global xBtn, yBtn, mines, nMoves, mrk
    mines = xBtn * yBtn * 10 // 64
    nMoves = 0
    mrk = 0
    playArea.clear()
    for b in btn:
        b.destroy()
    btn.clear()
    for f in frm:
        f.destroy()
    frm.clear()
    playground()

def playground():
    """Создание игрового поля."""
    global xBtn, yBtn
    for i in range(yBtn):
        frm.append(Frame())
        frm[i].pack(expand=YES, fill=BOTH)
        for j in range(xBtn):
            b = Button(frm[i], text=' ', font=('mono', 16, 'bold'),
                       width=2, height=1, padx=0, pady=0, bg='#999')  # Серый фон для неоткрытых
            b.config(command=lambda n=len(btn): play(n))
            b.bind('<Button-3>', lambda event, n=len(btn): mark_cell(n))  # Правый клик для флага
            b.pack(side=LEFT, expand=YES, fill=BOTH, padx=0, pady=0)
            btn.append(b)
            playArea.append(0)

# Инициализация игры
tk = Tk()
tk.title('Achtung, Minen!')
tk.geometry('800x700')  # Устанавливаем начальное разрешение окна

xBtn, yBtn = 16, 16
mines = xBtn * yBtn * 10 // 64
playArea = []
nMoves = 0
mrk = 0
imgMark, imgMine = '⚑', '💣'
frm, btn = [], []
playground()
mainloop()
