document.addEventListener('DOMContentLoaded', function() {
    const showMoreButton = document.getElementById('show-more');
    if (showMoreButton) {
        showMoreButton.addEventListener('click', function() {
            const genre = this.dataset.genre;
            const offset = parseInt(this.dataset.offset);
            let excludedIds = JSON.parse(this.dataset.excludedIds) || [];

            fetch('/show_more', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ genre: genre, offset: offset, excluded_ids: excludedIds })
            })
            .then(response => response.json())
            .then(data => {
                const gameList = document.getElementById('game-list') || document.getElementById('recommendations-list');
                data.recommendations.forEach(game => {
                    const listItem = document.createElement('li');
                    listItem.id = `game-${game.id}`;
                    listItem.innerHTML = `
                        <h2>${game.title}</h2>
                        <p>Genre: ${game.genre}</p>
                        <p>Year: ${game.year}</p>
                        <p>Developer: ${game.developer}</p>
                        <p>Publisher: ${game.publisher}</p>
                        <p>Platform: ${game.platform}</p>
                        <p>Critic Score: ${game.criticscore}</p>
                        <p>User Score: ${game.userscore}</p>
                        <img src="${game.poster}" alt="${game.title} poster" style="max-width: 200px;">
                        <button type="button" class="played-button" data-game-id="${game.id}" data-genre="${genre}" data-offset="${offset}" data-excluded-ids="${JSON.stringify(excludedIds)}">Уже играл</button>
                    `;
                    gameList.appendChild(listItem);
                    excludedIds.push(game.id);
                });
                this.dataset.offset = offset + data.recommendations.length;
                this.dataset.excludedIds = JSON.stringify(excludedIds);
            });
        });
    }

    document.addEventListener('click', function(event) {
        if (event.target && event.target.classList.contains('played-button')) {
            event.preventDefault(); // Предотвращение перезагрузки страницы
            const gameId = event.target.dataset.gameId;
            const genre = event.target.dataset.genre;
            const offset = parseInt(event.target.dataset.offset);
            let excludedIds = JSON.parse(event.target.dataset.excludedIds);

            console.log(`Marking game ${gameId} as played.`);

            // Удаление правильного элемента из списка
            const listItem = document.getElementById(`game-${gameId}`);
            if (listItem) {
                listItem.remove();
                console.log(`Removed game ${gameId} from the list.`);
            }

            // Обновление excludedIds
            if (!excludedIds.includes(gameId)) {
                excludedIds.push(gameId);
            }
            event.target.dataset.excludedIds = JSON.stringify(excludedIds);
            console.log(`Updated excludedIds: ${event.target.dataset.excludedIds}`);

            // Обновление кнопки "Show More"
            const showMoreButton = document.getElementById('show-more');
            if (showMoreButton) {
                let showMoreExcludedIds = JSON.parse(showMoreButton.dataset.excludedIds) || [];
                if (!showMoreExcludedIds.includes(gameId)) {
                    showMoreExcludedIds.push(gameId);
                    showMoreButton.dataset.excludedIds = JSON.stringify(showMoreExcludedIds);
                }
                console.log(`Updated showMoreButton excludedIds: ${showMoreButton.dataset.excludedIds}`);
            }

            fetch('/mark_played', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ game_id: gameId, genre: genre, offset: offset, excluded_ids: excludedIds })
            })
            .then(response => response.json())
            .then(data => {
                if (data.message) {
                    alert(data.message);
                } else {
                    const newListItem = document.createElement('li');
                    newListItem.id = `game-${data.id}`;
                    newListItem.innerHTML = `
                        <h2>${data.title}</h2>
                        <p>Genre: ${data.genre}</p>
                        <p>Year: ${data.year}</p>
                        <p>Developer: ${data.developer}</p>
                        <p>Publisher: ${data.publisher}</p>
                        <p>Platform: ${data.platform}</p>
                        <p>Critic Score: ${data.criticscore}</p>
                        <p>User Score: ${data.userscore}</p>
                        <img src="${data.poster}" alt="${data.title} poster" style="max-width: 200px;">
                        <button type="button" class="played-button" data-game-id="${data.id}" data-genre="${genre}" data-offset="${offset}" data-excluded-ids="${JSON.stringify(excludedIds)}">Уже играл</button>
                    `;
                    (document.getElementById('game-list') || document.getElementById('recommendations-list')).appendChild(newListItem);
                }
            });
        }
    });

    const searchForm = document.getElementById('search-form');
    if (searchForm) {
        searchForm.addEventListener('submit', function(event) {
            event.preventDefault();
            fetch(searchForm.action, {
                method: searchForm.method,
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded'
                },
                body: new URLSearchParams(new FormData(searchForm)).toString()
            })
            .then(response => response.text())
            .then(html => {
                document.open();
                document.write(html);
                document.close();
            });
        });
    }

    const recommendationForm = document.getElementById('recommendation-form');
    if (recommendationForm) {
        recommendationForm.addEventListener('submit', function(event) {
            event.preventDefault();
            fetch(recommendationForm.action, {
                method: recommendationForm.method,
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded'
                },
                body: new URLSearchParams(new FormData(recommendationForm)).toString()
            })
            .then(response => response.text())
            .then(html => {
                document.open();
                document.write(html);
                document.close();
            });
        });
    }
});
