#!/usr/bin/env python3
"""Interactive Review CLI - 웹 기반 질문/Plan 리뷰 UI"""

import argparse
import json
import os
import platform
import subprocess
import sys
import threading
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler

_result = None
_result_event = threading.Event()

# ---------------------------------------------------------------------------
# HTML Templates
# ---------------------------------------------------------------------------

QUESTIONS_HTML = r"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Interactive Review</title>
<style>
:root {
    --label-500: #17191c;
    --label-400: #525964;
    --label-300: #9aa3b2;
    --label-tertiary: #9aa3b2;
    --label-error: #ef5d5d;
    --label-success: #16c390;
    --icon-primarybrand: #3052df;
    --container-200: rgba(155,168,198,.16);
    --border-300: rgba(155,168,198,.16);
    --fixed-light: #ffffff;
    --radius-3: 3px;
    --radius-5: 5px;
    --spacing-xxs: 8px;
    --spacing-sm: 12px;
    --spacing-lg: 24px;
}
* { box-sizing: border-box; margin: 0; padding: 0; }
body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', sans-serif;
    background: #f5f6f8;
    color: var(--label-500);
    line-height: 1.5;
}
.container {
    max-width: 720px;
    margin: 0 auto;
    padding: 32px var(--spacing-lg);
}
.page-title {
    font-size: 20px;
    font-weight: 600;
    margin-bottom: var(--spacing-lg);
}
.card {
    background: var(--fixed-light);
    border: 1px solid var(--border-300);
    border-radius: var(--radius-5);
    padding: 20px;
    margin-bottom: 16px;
}
.card-header {
    display: flex;
    align-items: center;
    gap: var(--spacing-xxs);
    margin-bottom: var(--spacing-sm);
}
.header-chip {
    display: inline-block;
    background: var(--icon-primarybrand);
    color: var(--fixed-light);
    font-size: 11px;
    font-weight: 600;
    padding: 2px 8px;
    border-radius: var(--radius-3);
    text-transform: uppercase;
    letter-spacing: 0.5px;
}
.question-text {
    font-size: 15px;
    font-weight: 500;
    margin-bottom: 16px;
}
.options-group {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-xxs);
}
.option-item {
    display: flex;
    align-items: flex-start;
    gap: var(--spacing-xxs);
    padding: 10px var(--spacing-sm);
    border: 1px solid var(--border-300);
    border-radius: var(--radius-5);
    cursor: pointer;
    transition: all 0.15s ease;
}
.option-item:hover {
    background: var(--container-200);
}
.option-item.selected {
    border-color: var(--icon-primarybrand);
    background: rgba(48,82,223,0.04);
}
.option-item input[type="radio"],
.option-item input[type="checkbox"] {
    margin-top: 2px;
    accent-color: var(--icon-primarybrand);
}
.option-info { flex: 1; }
.option-label {
    font-size: 14px;
    font-weight: 500;
}
.option-desc {
    font-size: 13px;
    color: var(--label-tertiary);
    margin-top: 2px;
}
.other-input {
    width: 100%;
    padding: 8px var(--spacing-sm);
    border: 1px solid var(--border-300);
    border-radius: var(--radius-5);
    font-size: 14px;
    margin-top: 6px;
    display: none;
    outline: none;
    transition: border-color 0.15s ease;
}
.other-input:focus { border-color: var(--icon-primarybrand); }
.other-input.visible { display: block; }
textarea.free-text {
    width: 100%;
    min-height: 100px;
    padding: var(--spacing-sm);
    border: 1px solid var(--border-300);
    border-radius: var(--radius-5);
    font-size: 14px;
    font-family: inherit;
    resize: vertical;
    outline: none;
    transition: border-color 0.15s ease;
}
textarea.free-text:focus { border-color: var(--icon-primarybrand); }
.submit-area {
    margin-top: var(--spacing-lg);
    text-align: right;
}
.btn-submit {
    background: var(--icon-primarybrand);
    color: var(--fixed-light);
    border: none;
    padding: 10px 32px;
    border-radius: var(--radius-5);
    font-size: 14px;
    font-weight: 500;
    cursor: pointer;
    transition: opacity 0.15s ease;
}
.btn-submit:hover { opacity: 0.9; }
.btn-submit:disabled { opacity: 0.5; cursor: not-allowed; }
.submitted {
    text-align: center;
    padding: 64px 24px;
}
.submitted h2 {
    font-size: 20px;
    color: var(--label-success);
    margin-bottom: 8px;
}
.submitted p {
    color: var(--label-400);
    font-size: 14px;
}
</style>
</head>
<body>
<div class="container">
    <h1 class="page-title">Interactive Review</h1>
    <div id="questions"></div>
    <div class="submit-area">
        <button class="btn-submit" id="submitBtn" onclick="submitAnswers()">Submit</button>
    </div>
</div>
<script>
fetch('/api/data').then(r=>r.json()).then(data=>{renderQuestions(data.questions)});

function escapeHtml(t){
    var d=document.createElement('div');d.textContent=t;return d.innerHTML;
}

function renderQuestions(questions){
    var container=document.getElementById('questions');
    questions.forEach(function(q,i){
        var card=document.createElement('div');
        card.className='card';
        card.dataset.index=i;

        var headerHtml='';
        if(q.header){
            headerHtml='<div class="card-header"><span class="header-chip">'+escapeHtml(q.header)+'</span></div>';
        }

        var hasOptions=q.options&&q.options.length>0;
        var isMulti=q.multiSelect===true;
        var inputType=isMulti?'checkbox':'radio';
        var inputName='q'+i;
        var bodyHtml='';

        if(hasOptions){
            bodyHtml='<div class="options-group">';
            q.options.forEach(function(opt){
                var descHtml=opt.description?'<div class="option-desc">'+escapeHtml(opt.description)+'</div>':'';
                bodyHtml+='<label class="option-item" data-val="'+escapeHtml(opt.label)+'">'
                    +'<input type="'+inputType+'" name="'+inputName+'" value="'+escapeHtml(opt.label)+'" onchange="onOptionChange(this)">'
                    +'<div class="option-info"><div class="option-label">'+escapeHtml(opt.label)+'</div>'+descHtml+'</div></label>';
            });
            bodyHtml+='<label class="option-item" data-val="__other__">'
                +'<input type="'+inputType+'" name="'+inputName+'" value="__other__" onchange="onOptionChange(this)">'
                +'<div class="option-info"><div class="option-label">Other</div>'
                +'<input type="text" class="other-input" id="other-'+i+'" placeholder="직접 입력..."></div></label>';
            bodyHtml+='</div>';
        } else {
            bodyHtml='<textarea class="free-text" id="text-'+i+'" placeholder="답변을 입력하세요..."></textarea>';
        }

        card.innerHTML=headerHtml
            +'<div class="question-text">'+escapeHtml(q.question)+'</div>'
            +bodyHtml;
        container.appendChild(card);
    });
}

function onOptionChange(input){
    var label=input.closest('.option-item');
    var group=label.closest('.options-group');
    var isCheckbox=input.type==='checkbox';

    if(!isCheckbox){
        group.querySelectorAll('.option-item').forEach(function(o){o.classList.remove('selected')});
    }
    if(input.checked){label.classList.add('selected')}else{label.classList.remove('selected')}

    var otherInput=group.querySelector('.other-input');
    if(otherInput){
        var otherChecked=group.querySelector('input[value="__other__"]').checked;
        if(otherChecked){otherInput.classList.add('visible');if(label.dataset.val==='__other__')otherInput.focus()}
        else{otherInput.classList.remove('visible')}
    }
}

function submitAnswers(){
    var btn=document.getElementById('submitBtn');
    btn.disabled=true;btn.textContent='Submitting...';
    var cards=document.querySelectorAll('.card');
    var answers=[];

    cards.forEach(function(card,i){
        var q=card.querySelector('.question-text').textContent;
        var textarea=card.querySelector('.free-text');

        if(textarea){
            answers.push({id:'q'+i,question:q,type:'free_text',value:textarea.value});
        } else {
            var checked=card.querySelectorAll('input:checked');
            var isMulti=card.querySelector('input[type="checkbox"]')!==null;

            if(isMulti){
                var values=[];
                checked.forEach(function(c){
                    if(c.value==='__other__'){var oi=card.querySelector('.other-input');if(oi&&oi.value)values.push(oi.value)}
                    else{values.push(c.value)}
                });
                answers.push({id:'q'+i,question:q,type:'multi_select',value:values});
            } else {
                var value='';
                if(checked.length>0){
                    if(checked[0].value==='__other__'){var oi=card.querySelector('.other-input');value=oi?oi.value:''}
                    else{value=checked[0].value}
                }
                answers.push({id:'q'+i,question:q,type:'single_select',value:value});
            }
        }
    });

    fetch('/api/submit',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({answers:answers})})
    .then(function(){
        document.querySelector('.container').innerHTML='<div class="submitted"><h2>제출 완료</h2><p>응답이 전송되었습니다. 이 탭을 닫아도 됩니다.</p></div>';
    });
}
</script>
</body>
</html>"""

PLAN_REVIEW_HTML = r"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Plan Review</title>
<style>
:root {
    --label-500: #17191c;
    --label-400: #525964;
    --label-300: #9aa3b2;
    --label-tertiary: #9aa3b2;
    --label-error: #ef5d5d;
    --label-success: #16c390;
    --icon-primarybrand: #3052df;
    --container-200: rgba(155,168,198,.16);
    --border-300: rgba(155,168,198,.16);
    --fixed-light: #ffffff;
    --radius-3: 3px;
    --radius-5: 5px;
    --spacing-xxs: 8px;
    --spacing-sm: 12px;
    --spacing-lg: 24px;
}
* { box-sizing: border-box; margin: 0; padding: 0; }
body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', sans-serif;
    background: #f5f6f8;
    color: var(--label-500);
    line-height: 1.5;
}
.container {
    max-width: 960px;
    margin: 0 auto;
    padding: 32px var(--spacing-lg);
}
.page-header {
    display: flex;
    align-items: center;
    gap: var(--spacing-sm);
    margin-bottom: var(--spacing-lg);
}
.page-title { font-size: 20px; font-weight: 600; }
.filename {
    font-size: 13px;
    color: var(--label-400);
    background: var(--container-200);
    padding: 2px 8px;
    border-radius: var(--radius-3);
    font-family: 'SF Mono', Monaco, Menlo, Consolas, monospace;
}
.tabs {
    display: flex;
    border-bottom: 1px solid var(--border-300);
}
.tab-btn {
    padding: 8px 16px;
    background: none;
    border: none;
    border-bottom: 2px solid transparent;
    font-size: 14px;
    font-weight: 500;
    color: var(--label-400);
    cursor: pointer;
    transition: all 0.15s ease;
}
.tab-btn:hover { color: var(--label-500); }
.tab-btn.active {
    color: var(--icon-primarybrand);
    border-bottom-color: var(--icon-primarybrand);
}
.content-panel {
    background: var(--fixed-light);
    border: 1px solid var(--border-300);
    border-top: none;
    border-radius: 0 0 var(--radius-5) var(--radius-5);
    min-height: 300px;
}
/* Source view */
.source-view { overflow-x: auto; }
.line-row {
    display: flex;
    align-items: stretch;
    border-bottom: 1px solid rgba(155,168,198,0.08);
    position: relative;
}
.line-row:hover { background: var(--container-200); }
.line-row:hover .add-comment-btn { opacity: 1; }
.line-num {
    width: 50px;
    min-width: 50px;
    padding: 2px 8px 2px 0;
    text-align: right;
    font-family: 'SF Mono', Monaco, Menlo, Consolas, monospace;
    font-size: 12px;
    color: var(--label-300);
    user-select: none;
    border-right: 1px solid var(--border-300);
}
.line-content {
    flex: 1;
    padding: 2px 12px;
    font-family: 'SF Mono', Monaco, Menlo, Consolas, monospace;
    font-size: 13px;
    white-space: pre;
    tab-size: 4;
}
.add-comment-btn {
    position: absolute;
    left: 54px;
    top: 50%;
    transform: translateY(-50%);
    width: 20px;
    height: 20px;
    border-radius: 50%;
    background: var(--icon-primarybrand);
    color: var(--fixed-light);
    border: none;
    font-size: 14px;
    line-height: 20px;
    text-align: center;
    cursor: pointer;
    opacity: 0;
    transition: opacity 0.15s ease;
    z-index: 1;
}
.line-row.has-comment .line-num { background: rgba(48,82,223,0.06); }
/* Comment block */
.comment-block {
    padding: 12px 12px 12px 62px;
    background: rgba(48,82,223,0.03);
    border-left: 3px solid var(--icon-primarybrand);
}
.comment-block textarea {
    width: 100%;
    min-height: 60px;
    padding: var(--spacing-xxs);
    border: 1px solid var(--border-300);
    border-radius: var(--radius-3);
    font-size: 13px;
    font-family: inherit;
    resize: vertical;
    outline: none;
}
.comment-block textarea:focus { border-color: var(--icon-primarybrand); }
.comment-actions {
    display: flex;
    gap: 6px;
    margin-top: 6px;
    justify-content: flex-end;
}
.comment-actions button {
    padding: 4px 12px;
    border-radius: var(--radius-3);
    font-size: 12px;
    cursor: pointer;
    border: 1px solid var(--border-300);
    background: var(--fixed-light);
    color: var(--label-400);
}
.comment-actions .btn-save {
    background: var(--icon-primarybrand);
    color: var(--fixed-light);
    border-color: var(--icon-primarybrand);
}
.saved-comment {
    padding: 8px 12px 8px 62px;
    background: rgba(48,82,223,0.03);
    border-left: 3px solid var(--icon-primarybrand);
    font-size: 13px;
    display: flex;
    align-items: flex-start;
    gap: 8px;
}
.saved-comment .comment-text { flex: 1; white-space: pre-wrap; }
.saved-comment .edit-btn,
.saved-comment .delete-btn {
    background: none;
    border: none;
    color: var(--label-300);
    cursor: pointer;
    font-size: 12px;
    padding: 2px 4px;
}
.saved-comment .edit-btn:hover { color: var(--icon-primarybrand); }
.saved-comment .delete-btn:hover { color: var(--label-error); }
/* Preview view */
.preview-view {
    padding: var(--spacing-lg);
    display: none;
}
.preview-view h1, .preview-view h2, .preview-view h3, .preview-view h4 {
    margin-top: 20px;
    margin-bottom: 8px;
}
.preview-view h1 { font-size: 24px; }
.preview-view h2 { font-size: 20px; border-bottom: 1px solid var(--border-300); padding-bottom: 4px; }
.preview-view h3 { font-size: 16px; }
.preview-view p { margin-bottom: 12px; }
.preview-view code {
    background: var(--container-200);
    padding: 2px 6px;
    border-radius: var(--radius-3);
    font-family: 'SF Mono', Monaco, Menlo, Consolas, monospace;
    font-size: 13px;
}
.preview-view pre {
    background: #1e1e2e;
    color: #cdd6f4;
    padding: 16px;
    border-radius: var(--radius-5);
    overflow-x: auto;
    margin-bottom: 12px;
}
.preview-view pre code { background: none; padding: 0; color: inherit; }
.preview-view ul, .preview-view ol { margin-bottom: 12px; padding-left: 24px; }
.preview-view li { margin-bottom: 4px; }
.preview-view table { border-collapse: collapse; margin-bottom: 12px; width: 100%; }
.preview-view th, .preview-view td {
    border: 1px solid var(--border-300);
    padding: 6px 12px;
    text-align: left;
}
.preview-view th { background: var(--container-200); font-weight: 600; }
.preview-view blockquote {
    border-left: 3px solid var(--border-300);
    padding-left: 12px;
    color: var(--label-400);
    margin-bottom: 12px;
}
.preview-unavailable {
    color: var(--label-300);
    font-style: italic;
    padding: 24px;
    text-align: center;
}
/* Review footer */
.review-footer {
    margin-top: var(--spacing-lg);
    background: var(--fixed-light);
    border: 1px solid var(--border-300);
    border-radius: var(--radius-5);
    padding: 20px;
}
.review-footer h3 {
    font-size: 14px;
    font-weight: 600;
    margin-bottom: var(--spacing-xxs);
}
.review-footer textarea {
    width: 100%;
    min-height: 80px;
    padding: var(--spacing-sm);
    border: 1px solid var(--border-300);
    border-radius: var(--radius-5);
    font-size: 14px;
    font-family: inherit;
    resize: vertical;
    outline: none;
    margin-bottom: 16px;
}
.review-footer textarea:focus { border-color: var(--icon-primarybrand); }
.comment-count {
    font-size: 13px;
    color: var(--label-400);
    margin-bottom: 16px;
}
.action-buttons {
    display: flex;
    gap: var(--spacing-xxs);
    justify-content: flex-end;
}
.btn-approve {
    background: var(--label-success);
    color: var(--fixed-light);
    border: none;
    padding: 10px 24px;
    border-radius: var(--radius-5);
    font-size: 14px;
    font-weight: 500;
    cursor: pointer;
    transition: opacity 0.15s ease;
}
.btn-approve:hover { opacity: 0.9; }
.btn-changes {
    background: var(--label-error);
    color: var(--fixed-light);
    border: none;
    padding: 10px 24px;
    border-radius: var(--radius-5);
    font-size: 14px;
    font-weight: 500;
    cursor: pointer;
    transition: opacity 0.15s ease;
}
.btn-changes:hover { opacity: 0.9; }
.btn-approve:disabled, .btn-changes:disabled { opacity: 0.5; cursor: not-allowed; }
.submitted {
    text-align: center;
    padding: 64px 24px;
}
.submitted h2 { font-size: 20px; margin-bottom: 8px; }
.submitted.approved h2 { color: var(--label-success); }
.submitted.changes h2 { color: var(--label-error); }
.submitted p { color: var(--label-400); font-size: 14px; }
</style>
</head>
<body>
<div class="container">
    <div class="page-header">
        <h1 class="page-title">Plan Review</h1>
        <span class="filename" id="filename"></span>
    </div>
    <div class="tabs">
        <button class="tab-btn active" onclick="switchTab('source',this)">Source</button>
        <button class="tab-btn" onclick="switchTab('preview',this)">Preview</button>
    </div>
    <div class="content-panel">
        <div class="source-view" id="sourceView"></div>
        <div class="preview-view" id="previewView"></div>
    </div>
    <div class="review-footer">
        <div class="comment-count" id="commentCount">0 comments</div>
        <h3>General Comment</h3>
        <textarea id="generalComment" placeholder="전체적인 의견을 남겨주세요..."></textarea>
        <div class="action-buttons">
            <button class="btn-approve" onclick="submitReview('approved')">Approve</button>
            <button class="btn-changes" onclick="submitReview('changes_requested')">Request Changes</button>
        </div>
    </div>
</div>
<script async src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
<script>
var comments={};
var planContent='';

fetch('/api/data').then(function(r){return r.json()}).then(function(data){
    document.getElementById('filename').textContent=data.filename;
    planContent=data.content;
    renderSource(data.content);
});

function escapeHtml(t){
    var d=document.createElement('div');d.textContent=t;return d.innerHTML;
}

function renderSource(content){
    var lines=content.split('\n');
    var container=document.getElementById('sourceView');
    lines.forEach(function(line,i){
        var lineNum=i+1;
        var row=document.createElement('div');
        row.className='line-row';
        row.id='line-'+lineNum;

        var numEl=document.createElement('span');
        numEl.className='line-num';
        numEl.textContent=lineNum;

        var contentEl=document.createElement('span');
        contentEl.className='line-content';
        contentEl.textContent=line||' ';

        var addBtn=document.createElement('button');
        addBtn.className='add-comment-btn';
        addBtn.textContent='+';
        addBtn.setAttribute('data-line',lineNum);
        addBtn.onclick=function(){toggleCommentForm(lineNum)};

        row.appendChild(numEl);
        row.appendChild(contentEl);
        row.appendChild(addBtn);
        container.appendChild(row);
    });
}

function toggleCommentForm(lineNum){
    var existingForm=document.getElementById('comment-form-'+lineNum);
    if(existingForm){existingForm.remove();return}

    var existingSaved=document.getElementById('saved-comment-'+lineNum);
    if(existingSaved){
        existingSaved.remove();
        showCommentForm(lineNum,comments[lineNum]||'');
        return;
    }
    showCommentForm(lineNum,'');
}

function showCommentForm(lineNum,initialText){
    var lineRow=document.getElementById('line-'+lineNum);
    var form=document.createElement('div');
    form.className='comment-block';
    form.id='comment-form-'+lineNum;

    var textarea=document.createElement('textarea');
    textarea.value=initialText;
    textarea.placeholder='코멘트를 입력하세요...';
    textarea.onkeydown=function(e){
        if(e.key==='Enter'&&(e.ctrlKey||e.metaKey)){saveComment(lineNum)}
    };

    var actions=document.createElement('div');
    actions.className='comment-actions';

    var cancelBtn=document.createElement('button');
    cancelBtn.textContent='Cancel';
    cancelBtn.onclick=function(){
        form.remove();
        if(!comments[lineNum]){lineRow.classList.remove('has-comment')}
    };

    var saveBtn=document.createElement('button');
    saveBtn.className='btn-save';
    saveBtn.textContent='Save (Ctrl+Enter)';
    saveBtn.onclick=function(){saveComment(lineNum)};

    actions.appendChild(cancelBtn);
    actions.appendChild(saveBtn);
    form.appendChild(textarea);
    form.appendChild(actions);

    lineRow.insertAdjacentElement('afterend',form);
    lineRow.classList.add('has-comment');
    textarea.focus();
}

function saveComment(lineNum){
    var form=document.getElementById('comment-form-'+lineNum);
    var textarea=form.querySelector('textarea');
    var text=textarea.value.trim();
    var lineRow=document.getElementById('line-'+lineNum);
    form.remove();

    if(!text){
        delete comments[lineNum];
        lineRow.classList.remove('has-comment');
        updateCommentCount();
        return;
    }

    comments[lineNum]=text;
    lineRow.classList.add('has-comment');

    var existingSaved=document.getElementById('saved-comment-'+lineNum);
    if(existingSaved)existingSaved.remove();

    var saved=document.createElement('div');
    saved.className='saved-comment';
    saved.id='saved-comment-'+lineNum;

    var commentText=document.createElement('span');
    commentText.className='comment-text';
    commentText.textContent=text;

    var editBtn=document.createElement('button');
    editBtn.className='edit-btn';
    editBtn.textContent='Edit';
    editBtn.onclick=function(){
        saved.remove();
        showCommentForm(lineNum,comments[lineNum]||'');
    };

    var deleteBtn=document.createElement('button');
    deleteBtn.className='delete-btn';
    deleteBtn.textContent='Delete';
    deleteBtn.onclick=function(){
        delete comments[lineNum];
        saved.remove();
        lineRow.classList.remove('has-comment');
        updateCommentCount();
    };

    saved.appendChild(commentText);
    saved.appendChild(editBtn);
    saved.appendChild(deleteBtn);
    lineRow.insertAdjacentElement('afterend',saved);
    updateCommentCount();
}

function updateCommentCount(){
    var count=Object.keys(comments).length;
    document.getElementById('commentCount').textContent=count+' comment'+(count!==1?'s':'');
}

function switchTab(tab,btn){
    document.querySelectorAll('.tab-btn').forEach(function(b){b.classList.remove('active')});
    btn.classList.add('active');
    document.getElementById('sourceView').style.display=tab==='source'?'block':'none';
    document.getElementById('previewView').style.display=tab==='preview'?'block':'none';

    if(tab==='preview'&&!document.getElementById('previewView').dataset.rendered){
        renderPreview();
        document.getElementById('previewView').dataset.rendered='true';
    }
}

function renderPreview(){
    var container=document.getElementById('previewView');
    try{
        if(typeof marked!=='undefined'){
            container.innerHTML=marked.parse(planContent);
        } else {
            container.innerHTML='<div class="preview-unavailable">Markdown preview를 사용할 수 없습니다 (marked.js 로드 실패)</div><pre>'+escapeHtml(planContent)+'</pre>';
        }
    }catch(e){
        container.innerHTML='<pre>'+escapeHtml(planContent)+'</pre>';
    }
}

function submitReview(status){
    document.querySelectorAll('.btn-approve,.btn-changes').forEach(function(b){b.disabled=true});

    var result={
        status:status,
        comments:Object.keys(comments).map(function(line){
            return {line:parseInt(line),text:comments[line]};
        }).sort(function(a,b){return a.line-b.line}),
        general_comment:document.getElementById('generalComment').value
    };

    fetch('/api/submit',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(result)})
    .then(function(){
        var cls=status==='approved'?'approved':'changes';
        var msg=status==='approved'?'Plan이 승인되었습니다':'변경 요청이 전송되었습니다';
        document.querySelector('.container').innerHTML='<div class="submitted '+cls+'"><h2>'+msg+'</h2><p>이 탭을 닫아도 됩니다.</p></div>';
    });
}
</script>
</body>
</html>"""

# ---------------------------------------------------------------------------
# HTTP Handler
# ---------------------------------------------------------------------------

class ReviewHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            html = QUESTIONS_HTML if self.server.mode == "questions" else PLAN_REVIEW_HTML
            self._send(200, "text/html; charset=utf-8", html.encode("utf-8"))
        elif self.path == "/api/data":
            body = json.dumps(self.server.data, ensure_ascii=False).encode("utf-8")
            self._send(200, "application/json; charset=utf-8", body)
        else:
            self.send_error(404)

    def do_POST(self):
        if self.path == "/api/submit":
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length)
            global _result
            _result = json.loads(body)
            _result_event.set()
            self._send(200, "application/json", b'{"ok":true}')
        else:
            self.send_error(404)

    def _send(self, code, content_type, body):
        try:
            self.send_response(code)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()
            self.wfile.write(body)
        except BrokenPipeError:
            pass

    def log_message(self, format, *args):
        pass  # suppress access logs


# ---------------------------------------------------------------------------
# Server & Browser
# ---------------------------------------------------------------------------

def open_browser(url):
    """브라우저 열기. WSL2 환경에서는 cmd.exe fallback 사용."""
    # WSL2: cmd.exe를 우선 시도 (webbrowser.open이 False 반환하는 환경)
    if "microsoft" in platform.uname().release.lower():
        try:
            subprocess.run(["cmd.exe", "/c", "start", url], check=False,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return
        except Exception:
            pass

    try:
        if webbrowser.open(url):
            return
    except Exception:
        pass

    print(f"브라우저를 열 수 없습니다. 직접 열어주세요: {url}", file=sys.stderr)


def run_server(mode, data, port=0, timeout=1800):
    server = HTTPServer(("127.0.0.1", port), ReviewHandler)
    server.mode = mode
    server.data = data

    actual_port = server.server_address[1]
    url = f"http://127.0.0.1:{actual_port}"

    print(f"서버 시작: {url}", file=sys.stderr)

    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()

    threading.Thread(target=open_browser, args=(url,), daemon=True).start()

    if _result_event.wait(timeout=timeout):
        server.shutdown()
        print(json.dumps(_result, ensure_ascii=False, indent=2))
    else:
        server.shutdown()
        print(json.dumps({"error": "timeout"}, ensure_ascii=False))
        sys.exit(1)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    p = argparse.ArgumentParser(description="Interactive Review CLI - 웹 기반 질문/Plan 리뷰 UI")
    sp = p.add_subparsers(dest="cmd", required=True)

    q = sp.add_parser("questions", help="질문 모드: 여러 질문을 웹 UI로 표시")
    q.add_argument("--data", help="질문 JSON 문자열")
    q.add_argument("--data-file", help="질문 JSON 파일 경로 (--data 대체)")
    q.add_argument("--port", type=int, default=0, help="서버 포트 (기본: OS 자동 할당)")
    q.add_argument("--timeout", type=int, default=1800, help="응답 대기 timeout 초 (기본: 1800)")

    pr = sp.add_parser("plan-review", help="Plan 리뷰 모드: Markdown 파일을 PR 리뷰 스타일로 검토")
    pr.add_argument("--file", required=True, help="리뷰할 Markdown 파일 경로")
    pr.add_argument("--port", type=int, default=0, help="서버 포트 (기본: OS 자동 할당)")
    pr.add_argument("--timeout", type=int, default=1800, help="응답 대기 timeout 초 (기본: 1800)")

    a = p.parse_args()

    if a.cmd == "questions":
        if a.data:
            data = json.loads(a.data)
        elif a.data_file:
            with open(a.data_file, encoding="utf-8") as f:
                data = json.load(f)
        else:
            print(json.dumps({"error": "--data or --data-file required"}))
            sys.exit(1)
        run_server("questions", data, a.port, a.timeout)

    elif a.cmd == "plan-review":
        with open(a.file, encoding="utf-8") as f:
            content = f.read()
        data = {"content": content, "filename": os.path.basename(a.file)}
        run_server("plan-review", data, a.port, a.timeout)


if __name__ == "__main__":
    main()
