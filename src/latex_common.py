"""Shared LaTeX-generation helpers: escaping, tables, and document preamble."""
import re

SPECIALS = {
    "&": r"\&", "%": r"\%", "$": r"\$", "#": r"\#", "_": r"\_",
    "{": r"\{", "}": r"\}", "~": r"\textasciitilde{}", "^": r"\textasciicircum{}",
    "\\": r"\textbackslash{}",
}


def esc(text) -> str:
    """Escape a plain-text string for LaTeX. HTML-ish <b> tags become \\textbf.
    An invisible break opportunity is inserted after every '/' so that
    slash-separated terms (e.g. 27701/27017/27018) can wrap in narrow cells."""
    s = str(text)
    s = s.replace("<b>", "\x01B1").replace("</b>", "\x01B0")
    s = s.replace("<i>", "\x01I1").replace("</i>", "\x01I0")
    out = []
    for ch in s:
        out.append(SPECIALS.get(ch, ch))
    s = "".join(out)
    s = s.replace("\x01B1", r"\textbf{").replace("\x01B0", "}")
    s = s.replace("\x01I1", r"\textit{").replace("\x01I0", "}")
    s = s.replace("/", r"/\slb{}")
    return s


def esc_plain(text) -> str:
    """Escape without interpreting <b>/<i> markup (for raw data fields)."""
    s = str(text)
    out = []
    for ch in s:
        out.append(SPECIALS.get(ch, ch))
    return "".join(out)


PREAMBLE = r"""
\documentclass[11pt,a4paper]{report}
\usepackage[a4paper,margin=25.4mm,headheight=14pt]{geometry}
\usepackage[T1]{fontenc}
\usepackage[utf8]{inputenc}
\usepackage[english]{babel}
\usepackage[expansion=false]{microtype}

\usepackage{parskip}
\usepackage{booktabs}
\usepackage{longtable}
\usepackage{tabularx}
\usepackage{array}
\usepackage{multirow}
\usepackage{colortbl}
\usepackage{xcolor}
\usepackage{fancyhdr}
\usepackage{titlesec}
\usepackage{enumitem}
\usepackage{caption}
\usepackage{graphicx}
\usepackage[hidelinks]{hyperref}
\usepackage{xurl}
\usepackage{seqsplit}
\usepackage{titletoc}

\definecolor{gy10}{gray}{0.90}
\definecolor{gy20}{gray}{0.82}
\definecolor{gy30}{gray}{0.74}
\definecolor{gy45}{gray}{0.60}
\definecolor{gy60}{gray}{0.45}
\definecolor{gyhead}{gray}{0.15}

\setlength{\parindent}{0pt}
\setlength{\parskip}{6pt}
\setlength{\tabcolsep}{3pt}
\renewcommand{\arraystretch}{1.15}
\sloppy

\titleformat{\chapter}[block]
  {\normalfont\Large\bfseries}{\thechapter.}{0.6em}{}
\titlespacing{\chapter}{0pt}{6pt}{18pt}
\titleformat{\section}{\normalfont\large\bfseries}{\thesection}{0.7em}{}
\titlespacing{\section}{0pt}{14pt}{6pt}
\titleformat{\subsection}{\normalfont\normalsize\bfseries}{\thesubsection}{0.7em}{}
\titlespacing{\subsection}{0pt}{10pt}{4pt}
\titleformat{\subsubsection}[runin]{\normalfont\normalsize\bfseries}{}{0em}{}[.\ ]
\titlespacing{\subsubsection}{0pt}{8pt}{4pt}

\pagestyle{fancy}
\fancyhf{}
\renewcommand{\headrulewidth}{0.4pt}
\renewcommand{\footrulewidth}{0.4pt}
\fancyfoot[C]{\thepage}

\setlist[itemize]{leftmargin=1.4em, itemsep=2pt, topsep=2pt}
\setlist[enumerate]{leftmargin=1.6em, itemsep=2pt, topsep=2pt}

\newcommand{\slb}{\discretionary{}{}{}}
\newcolumntype{L}[1]{>{\raggedright\arraybackslash}p{#1}}
\newcolumntype{C}[1]{>{\centering\arraybackslash}p{#1}}

\newcommand{\ratingcell}[1]{%
  \ifnum#1<5 \cellcolor{gy10}#1%
  \else\ifnum#1<13 \cellcolor{gy20}#1%
  \else\ifnum#1<20 \cellcolor{gy45}\textcolor{white}{#1}%
  \else \cellcolor{gyhead}\textcolor{white}{#1}%
  \fi\fi\fi}

\newenvironment{note}
  {\begin{quote}\small\itshape}
  {\end{quote}}
"""


def fancy_header(left: str, right: str = "") -> str:
    return rf"""\fancyhead[L]{{\footnotesize {left}}}
\fancyhead[R]{{\footnotesize {right}}}
"""


def longtable_str(header, rows, colspec, caption=None, label=None, small=True, header_rule=True, zebra=True):
    """header: list of str; rows: list of list of str (already LaTeX-escaped); colspec e.g. 'L{4cm} L{3cm}'"""
    size = r"\small" if small else ""
    out = []
    if caption:
        out.append(rf"\begin{{longtable}}{{{colspec}}}")
        out.append(rf"\caption{{{caption}}}" + (rf"\label{{{label}}}" if label else "") + r"\\")
    else:
        out.append(rf"\begin{{longtable}}{{{colspec}}}")
    out.append(r"\toprule")
    hdr = " & ".join([rf"\textbf{{\textcolor{{white}}{{{h}}}}}" for h in header]) + r" \\"
    out.append(r"\rowcolor{gyhead}" + hdr)
    out.append(r"\midrule")
    out.append(r"\endfirsthead")
    out.append(r"\toprule")
    out.append(r"\rowcolor{gyhead}" + hdr)
    out.append(r"\midrule")
    out.append(r"\endhead")
    out.append(r"\bottomrule")
    out.append(r"\endfoot")
    for i, row in enumerate(rows):
        bg = (r"\rowcolor{gy10}" if (i % 2 == 1) else "") if zebra else ""
        out.append(bg + " & ".join(row) + r" \\")
    out.append(r"\end{longtable}")
    return size + "\n" + "\n".join(out) + ("\n\\normalsize" if small else "")
