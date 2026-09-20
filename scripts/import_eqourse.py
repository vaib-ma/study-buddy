#!/usr/bin/env python3
"""Import eQOURSE CC BY 4.0 JEE datasets into Study Buddy."""
from pathlib import Path
import argparse, json, re, urllib.request

ROOT=Path(__file__).resolve().parents[1]
BASE='https://huggingface.co/datasets/eQOURSE'
SUBJECTS={'physics':'Physics','chemistry':'Chemistry','mathematics':'Mathematics'}

def get_rows(url):
    with urllib.request.urlopen(url, timeout=60) as r:
        return [json.loads(x) for x in r.read().decode().splitlines() if x.strip()]

def year(source):
    m=re.findall(r'20\\d{2}', source or '')
    if m: return int(m[-1])
    m=re.findall(r'(?<!\\d)(\\d{2})(?!\\d)', source or '')
    return 2000+int(m[-1]) if m else 2000

def chapter(subject, topic, subtopic):
    t=(topic+' '+subtopic).lower()
    groups={
      'Physics':[('kinematic motion projectile','Kinematics'),('newton friction laws of motion','Laws of Motion'),('work energy power','Work, Energy and Power'),('rotation rolling moment of inertia','Rotational Motion'),('gravitation satellite','Gravitation'),('thermodynamic heat','Thermodynamics'),('oscillation harmonic','Oscillations'),('wave sound','Waves'),('electrostatic electric field capacitor','Electrostatics'),('current circuit resistance','Current Electricity'),('magnetic magnetism','Magnetic Effects of Current and Magnetism'),('induction alternating','Electromagnetic Induction and Alternating Current'),('optics','Optics'),('nuclear atom','Atoms and Nuclei')],
      'Chemistry':[('thermodynamic','Thermodynamics'),('equilibrium','Equilibrium'),('electrochem','Electrochemistry'),('kinetics','Chemical Kinetics'),('coordination','Coordination Compounds'),('hydrocarbon organic','Organic Chemistry'),('carbonyl aldehyde ketone carboxylic','Aldehydes, Ketones and Carboxylic Acids'),('amine nitrogen','Amines'),('atomic quantum','Structure of Atom'),('bond molecular','Chemical Bonding and Molecular Structure'),('periodic','Classification of Elements and Periodicity')],
      'Mathematics':[('complex','Complex Numbers'),('quadratic','Quadratic Equations'),('sequence progression series','Sequences and Series'),('binomial','Binomial Theorem'),('permutation combination','Permutations and Combinations'),('probability','Probability'),('matrix determinant','Matrices and Determinants'),('circle','Circle'),('conic parabola ellipse hyperbola','Conic Sections'),('vector','Vector Algebra'),('three dimensional plane','Three Dimensional Geometry'),('limit continuity','Limits and Continuity'),('differenti derivative','Differential Calculus'),('integral','Integral Calculus'),('trigonometric trigonometry','Trigonometry')]
    }
    for keys,name in groups.get(subject,[]):
        if any(k in t for k in keys.split()): return name
    return topic.strip() or 'Uncategorized'

def main():
    p=argparse.ArgumentParser(); p.add_argument('--advanced',action='store_true'); p.add_argument('--main',action='store_true'); a=p.parse_args()
    if not (a.advanced or a.main): p.error('choose --advanced and/or --main')
    jobs=[]
    if a.advanced: jobs.append(('JEE Advanced','jee-advanced-questions','jee_advanced'))
    if a.main: jobs.append(('JEE Main','jee-main-questions','jee_main'))
    for exam,dataset,outdir in jobs:
      for slug,subject in SUBJECTS.items():
        questions=[]; solutions=[]; n=0
        for split in ('train','test'):
          rows=get_rows(f'{BASE}/{dataset}/resolve/main/{slug}/{split}.jsonl')
          for row in rows:
            n+=1; opts=[row.get(f'option_{i}','').strip() for i in range(1,5)]; opts=[x for x in opts if x]
            qt=row.get('question_type','');
            if qt=='single_correct' and row.get('correct_option'): ans=opts[int(row['correct_option'])-1]; typ='MCQ'
            else: ans=str(row.get('numerical_answer') or row.get('answer') or '').strip(); typ='Numerical' if qt=='numerical' else 'Subjective'
            if not ans or not row.get('question'): continue
            y=year(row.get('source_paper','')); qid=f"{'JEEA' if exam=='JEE Advanced' else 'JEEM'}-{'PHY' if subject=='Physics' else 'CHE' if subject=='Chemistry' else 'MAT'}-{y:04d}-{n:06d}"
            ref=f'{BASE}/{dataset}'
            q={'question_id':qid,'exam':exam,'exam_year':y,'subject':subject,'chapter':chapter(subject,row.get('topic',''),row.get('subtopic','')),'topic':row.get('subtopic') or row.get('topic') or 'Uncategorized','difficulty':'Very Hard' if exam=='JEE Advanced' else 'Hard','question_type':typ,'question_text':row['question'].replace('[IMAGE]','\\n[Diagram]\\n'),'correct_answer':ans,'marks':4,'negative_marks':1 if typ=='MCQ' else 0,'source':'eQOURSE','source_reference':ref,'tags':['eQOURSE','CC BY 4.0',row.get('topic',''),row.get('subtopic','')],'content_type':'open_license','rights_status':'open_license','redistribution_allowed':True,'rights_holder':'eQOURSE','license':'CC BY 4.0','license_reference':ref}
            s={'question_id':qid,'solution_type':'source_worked_solution','solution_text':(row.get('solution') or 'No solution text supplied.').replace('[IMAGE]','\\n[Diagram]\\n'),'final_answer':ans,'key_concepts':[row.get('topic',''),row.get('subtopic','')],'source':'eQOURSE','source_reference':ref}
            questions.append(q); solutions.append(s)
        qp=ROOT/'data/questions'/outdir/f'{slug}.json'; sp=ROOT/'data/solutions'/outdir/f'{slug}.json'; qp.parent.mkdir(parents=True,exist_ok=True); sp.parent.mkdir(parents=True,exist_ok=True)
        qp.write_text(json.dumps(questions,indent=2,ensure_ascii=False)+'\\n'); sp.write_text(json.dumps(solutions,indent=2,ensure_ascii=False)+'\\n')
        print(exam,subject,len(questions))
if __name__=='__main__': main()