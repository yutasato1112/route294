window.onload = function() {
    const maxHeight = 1122; // 297mm = 1122px @96dpiの前提
    const containers = document.querySelectorAll('.preview_container');

    containers.forEach(container => {
        let currentHeight = container.offsetHeight;

        if (currentHeight > maxHeight) {
            // コンテナの子要素を一つずつ移動
            const children = Array.from(container.children);
            let newContainer = null;
            let tempHeight = 0;

            for (let i = 0; i < children.length; i++) {
                const child = children[i];
                tempHeight += child.offsetHeight;

                if (tempHeight > maxHeight) {
                    if (!newContainer) {
                        newContainer = document.createElement('div');
                        newContainer.classList.add('preview_container');
                        container.after(newContainer);
                    }
                    newContainer.appendChild(child);
                }
            }
        }
    });
};
