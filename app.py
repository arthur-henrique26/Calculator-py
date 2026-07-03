import tkinter as tk
from tkinter import messagebox
import math
import re

class Calculadora(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Calculadora Científica')
        self.resizable(False, False)
        self.configure(bg='black')
        self._value = tk.StringVar()

        self._create_widgets()

    def _create_widgets(self):
        # display
        frm_display = tk.Frame(self, bg='black', padx=8, pady=8)
        frm_display.grid(row=0, column=0, columnspan=6)
        entry = tk.Entry(frm_display, textvariable=self._value, justify='right',
            font=('Segoe UI', 20), width=28, bg='black', fg='red', insertbackground='red', bd=0)
        entry.grid(row=0, column=0)
        entry.focus()
        entry.bind('<Return>', lambda e: self._calculate())
        entry.bind('<BackSpace>', lambda e: None)

        # buttons layout (black background, red text)
        btn_cfg = {'bg':'#0b0b0b','fg':'#ff3333','activebackground':'#ff3333','activeforeground':'white','bd':1,'width':6,'height':2,'font':('Segoe UI',10)}

        buttons = [
            ('C', 1, 0), ('⌫', 1, 1), ('(', 1, 2), (')', 1, 3), ('%', 1, 4), ('÷', 1, 5),
            ('sin', 2, 0), ('cos', 2, 1), ('tan', 2, 2), ('ln', 2, 3), ('log', 2, 4), ('×', 2, 5),
            ('asin', 3, 0), ('acos', 3, 1), ('atan', 3, 2), ('√', 3, 3), ('^', 3, 4), ('!', 3, 5),
            ('7', 4, 0), ('8', 4, 1), ('9', 4, 2), ('4', 5, 0), ('5', 5, 1), ('6', 5, 2),
            ('-', 4, 3), ('pi', 4, 4), ('e', 4, 5),
            ('1', 6, 0), ('2', 6, 1), ('3', 6, 2), ('0', 7, 1), ('.', 6, 3), ('±', 6, 4),
            ('+', 5, 3), ('exp', 5, 4), ('%', 5, 5),
            ('=', 7, 3),
        ]

        frm_buttons = tk.Frame(self, bg='black', padx=8, pady=8)
        frm_buttons.grid(row=1, column=0)

        for (txt, r, c) in buttons:
            btn = tk.Button(frm_buttons, text=txt, command=lambda t=txt: self._on_click(t), **btn_cfg)
            btn.grid(row=r, column=c, padx=4, pady=4)

    def _on_click(self, char):
        if char == 'C':
            self._value.set('')
            return
        if char == '⌫':
            self._value.set(self._value.get()[:-1])
            return
        if char == '=':
            self._calculate()
            return
        if char == '±':
            self._toggle_sign()
            return
        if char == '%':
            # percent: convert current number to percent
            try:
                val = float(self._value.get())
                self._value.set(str(val/100))
            except Exception:
                pass
            return

        # map some buttons to function text
        map_funcs = {
            'sin':'sin(', 'cos':'cos(', 'tan':'tan(',
            'asin':'asin(', 'acos':'acos(', 'atan':'atan(',
            'ln':'ln(', 'log':'log(', 'sqrt':'sqrt(', '√':'sqrt(',
            'exp':'exp(', 'pi':'pi', 'e':'e'
        }
        if char in map_funcs:
            self._value.set(self._value.get() + map_funcs[char])
            return

        # factorial and power symbols appended as-is or special char '^' for power
        if char == '!':
            self._value.set(self._value.get() + '!')
            return

        # append numbers and operators (including × ÷ ^)
        self._value.set(self._value.get() + char)

    def _toggle_sign(self):
        v = self._value.get()
        if not v:
            return
        try:
            if v.startswith('-'):
                self._value.set(v[1:])
            else:
                self._value.set('-' + v)
        except Exception:
            pass

    def _calculate(self):
        expr = self._value.get()
        if not expr:
            return
        try:
            # preprocessing
            expr = expr.replace('×', '*').replace('÷', '/').replace('^', '**').replace('π', 'pi')
            # replace postfix factorial like 5! -> fact(5)
            expr = re.sub(r'(\d+(\.\d+)?)!', r'fact(\1)', expr)
            # allow 'ln(' -> natural log, 'log(' -> base10
            # prepare allowed names
            allowed_names = {k: getattr(math, k) for k in dir(math) if not k.startswith('_')}
            # add aliases and safe wrappers
            allowed_names.update({
                'sin': math.sin, 'cos': math.cos, 'tan': math.tan,
                'asin': math.asin, 'acos': math.acos, 'atan': math.atan,
                'log': math.log10, 'ln': math.log, 'sqrt': math.sqrt,
                'exp': math.exp,
                'pi': math.pi, 'e': math.e,
                'abs': abs, 'round': round,
                'pow': pow,
                'fact': lambda x: math.factorial(int(x)),
            })
            # evaluate safely
            result = eval(expr, {'__builtins__': None}, allowed_names)
            self._value.set(str(result))
        except Exception:
            messagebox.showerror('Erro', 'Expressão inválida')

if __name__ == '__main__':
    app = Calculadora()
    app.mainloop()
