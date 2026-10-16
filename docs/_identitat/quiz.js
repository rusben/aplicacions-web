  // Dissuasió de la còpia: mai al codi, a les taules ni dins de l'editor.
  // L'alumnat treballa per SSH i ha de poder enganxar les ordres.
  (function () {
    var LLIURE = 'pre, code, .cq-table, [contenteditable="true"]';
    function copiable(node) {
      if (node && node.nodeType !== 1) { node = node.parentNode; }
      return !!(node && node.closest && node.closest(LLIURE));
    }
    function seleccioCopiable() {
      var s = document.getSelection();
      if (!s || s.rangeCount === 0) { return false; }
      return copiable(s.getRangeAt(0).commonAncestorContainer);
    }
    ['copy', 'cut'].forEach(function (nom) {
      document.addEventListener(nom, function (e) {
        if (!seleccioCopiable()) { e.preventDefault(); }
      });
    });
    document.addEventListener('dragstart', function (e) {
      if (!copiable(e.target)) { e.preventDefault(); }
    });
  })();

  // Motor únic per a totes les preguntes single i multi.
  document.querySelectorAll('.cq-question').forEach(function (question) {
    var id = question.dataset.id;
    if (!id) {
      throw new Error('Falta data-id a una pregunta del quiz.');
    }
    var type = question.dataset.type;
    if (type !== 'single' && type !== 'multi') {
      throw new Error('data-type invàlid ("' + type + '") a la pregunta "' + id + '".');
    }

    var options = question.querySelectorAll('.cq-option');
    var checkBtn = question.querySelector('.cq-check-btn');
    var feedback = question.querySelector('.cq-feedback');

    options.forEach(function (opt) {
      opt.addEventListener('click', function () {
        if (type === 'single') {
          options.forEach(function (o) { o.classList.remove('cq-selected'); });
          opt.classList.add('cq-selected');
        } else {
          opt.classList.toggle('cq-selected');
        }
        options.forEach(function (o) {
          o.setAttribute('aria-pressed',
            o.classList.contains('cq-selected') ? 'true' : 'false');
        });
      });
    });

    checkBtn.addEventListener('click', function () {
      var allCorrect = true;
      options.forEach(function (opt) {
        var isCorrect = opt.dataset.correct === 'true';
        var isSelected = opt.classList.contains('cq-selected');
        opt.classList.remove('cq-selected');
        opt.setAttribute('aria-pressed', 'false');
        if (isCorrect) {
          opt.classList.add('cq-correct');
        } else if (isSelected) {
          opt.classList.add('cq-incorrect');
        }
        opt.disabled = true;
        if (isCorrect !== isSelected) {
          allCorrect = false;
        }
      });
      feedback.textContent = allCorrect ? 'Correcte!' : 'Incorrecte, revisa les respostes marcades.';
      feedback.className = 'cq-feedback ' + (allCorrect ? 'ok' : 'ko');
      checkBtn.disabled = true;
    });
  });
