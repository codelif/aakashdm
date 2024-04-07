// function toggle_img_dark(params) {

//   :q
//   
// }


let answer = document.querySelectorAll(".choice-group")
answer.forEach((v) => {
v.addEventListener("click", (event) => {
  let target = event.target
  count = 0
  while (target.nodeName != "SL-CARD") {
    target = target.parentElement
    if (count == 10) break
    count++;
  }

  if (parseInt(target.attributes.value.value) === parseInt(get_answer(target))){
    notify("Your answer is correct!", "success")
  }else{
    notify("Your answer is incorrect!", "warning")
  }

})

})


function get_answer(child_element) {
  let target = child_element

  while (true){
    if (target.nodeName == "DIV" && target.classList.contains("answer")) {
      return target.attributes.value.value
    }

    target = target.parentElement
  }
}

function escapeHtml(html) {
  const div = document.createElement('div');
  div.textContent = html;
  return div.innerHTML;
}

// Custom function to emit toast notifications
function notify(message, variant = 'primary', icon = 'info-circle', duration = 3000) {
  const alert = Object.assign(document.createElement('sl-alert'), {
    variant,
    closable: true,
    duration: duration,
    innerHTML: `
        <sl-icon name="${icon}" slot="icon"></sl-icon>
        ${escapeHtml(message)}
      `
  });

  document.body.append(alert);
  return alert.toast();
}
