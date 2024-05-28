function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function main() {
    console.log('TEST')
    const likeElements = document.querySelectorAll('.answer-like-control')
    for (const one_element of likeElements) {
        const likeButton = one_element.getElementsByClassName('like-btn')[0]
        const dislikeButton = one_element.getElementsByClassName('dislike-btn')[0]
        const count = one_element.getElementsByClassName('like-counter')[0]
        const answer = one_element.dataset.answerId

        function likeOrDislike(isLike) {
            console.log('тык')
            const request = new Request('/like-answer/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({
                    answerId: answer,
                    isLike: isLike
                })
            })

            fetch(request)
                .then((response) => response.json())
                .then((data) => {
                    count.innerHTML = data.rating
                })
        }

        likeButton.onclick = () => likeOrDislike(true)
        dislikeButton.onclick = () => likeOrDislike(false)
    }

    const questionId = document.querySelector('.question-like-control').dataset.questionId
    const correctAnswerCheckboxes = document.querySelectorAll('.correct-answer-checkbox')
    for (const checkbox of correctAnswerCheckboxes) {
        const answerId = checkbox.dataset.answerId
        checkbox.onchange = () => {
            const request = new Request(`/mark-answer/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({
                    questionId: questionId,
                    answerId: answerId,
                    isCorrect: checkbox.checked
                })
            })
            fetch(request)
        }
    }
}

main()