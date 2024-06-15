function showlist() {
    var input, filter;
    input = document.getElementById("search-input");
    filter = input.value.trim();
    if (filter === "") {
        search();
    }


    }


function handleKeyDown(event) {
    if (event.keyCode === 13) { // 13 表示回车键
        event.preventDefault(); // 阻止默认的提交行为
        search(); // 调用搜索函数
    }
}




function search() {
    var input, filter, table, tr, td, i, txtValue;
    input = document.getElementById("search-input");
    filter = input.value.toUpperCase();
    table = document.getElementById("file-table");
    tr = table.getElementsByTagName("tr");

    for (i = 1; i < tr.length; i++) { // 从索引1开始，跳过表头行
        td = tr[i].getElementsByClassName("name-column")[0];
        if (td) {
            txtValue = td.textContent || td.innerText;
            if (txtValue.toUpperCase().indexOf(filter) > -1) {
                tr[i].style.display = "";
            } else {
                tr[i].style.display = "none";
            }
        }
    }

    // 重新计算分页链接的显示
    var pagination = document.getElementsByClassName("pagination")[0];
    var visibleRows = table.querySelectorAll("tr:not([style*='display: none'])").length;
    var totalPages = Math.ceil(visibleRows / 50);

    if (totalPages > 1) {
        pagination.style.display = "block";
    } else {
        pagination.style.display = "none";
    }

    // 清空搜索框时重定向页面
    if (filter === "") {
        location.reload();
        return;  // 添加这一行，避免发送空搜索请求到后端
    }

    // 发送搜索请求到后端
    var xhr = new XMLHttpRequest();
    xhr.open("GET", "/search?keyword=" + encodeURIComponent(filter), true);
    xhr.onreadystatechange = function() {
        if (xhr.readyState === 4 && xhr.status === 200) {
            var plistInfo = JSON.parse(xhr.responseText);
            // 清空现有数据
            tbody.innerHTML = '';
            // 添加新行数据
            updateFileTable(plistInfo);
        }
    };
    xhr.send();
}



function updateFileTable(plistInfo) {
    var table = document.getElementById('file-table');
    var tbody = table.querySelector('tbody');
    var rows = tbody.getElementsByTagName('tr');

//     Remove existing rows
    for (var i = rows.length - 1; i >= 0; i--) {
       tbody.removeChild(rows[i]);
    }

    // Add new rows based on plistInfo
    for (var i = 0; i < plistInfo.length; i++) {
        var plist = plistInfo[i];

        var row = document.createElement('tr');
        var checkboxCell = document.createElement('td');
        checkboxCell.className = 'checkbox-cell'
        var checkbox = document.createElement('input');
        checkbox.type = 'checkbox';
        checkbox.className = 'checkbox-cell'
        checkbox.name = 'file-checkbox';
        checkbox.value = plist.filename;
        checkboxCell.appendChild(checkbox);

        var nameCell = document.createElement('td');
        nameCell.className = 'name-column';
        nameCell.textContent = plist.title.replace('<string>', '');

        var buttonCell = document.createElement('td');
        buttonCell.className = 'button-column';
        var installButton = document.createElement('a');
        installButton.href = 'itms-services://?action=download-manifest&url=' +plist.domain + '/plist/' + plist.filename;
        installButton.className = 'install-button';
        installButton.textContent = '安装';
        var downloadButton = document.createElement('a');
        downloadButton.href = '/download_file/' + plist.filename;
        downloadButton.className = 'download-button';
        downloadButton.textContent = '下载';
        var deleteButton = document.createElement('a');
        deleteButton.href = '/delete_plist/' + plist.filename;
        deleteButton.className = 'delete-button';
        deleteButton.textContent = '删除';
        deleteButton.addEventListener('click', function () {
            confirmDelete(plist.filename); // 添加点击事件，调用确认删除函数
        });
        buttonCell.appendChild(installButton);
        buttonCell.appendChild(downloadButton);
        buttonCell.appendChild(deleteButton);

        row.appendChild(checkboxCell);
        row.appendChild(nameCell);
        row.appendChild(buttonCell);

        tbody.appendChild(row);
    }
}



        function editSelected() {
            var checkboxes = document.getElementsByName("file-checkbox");
            var selectedCount = 0;
            var selectedFilename = "";

            for (var i = 0; i < checkboxes.length; i++) {
                if (checkboxes[i].checked) {
                    selectedCount++;
                    selectedFilename = checkboxes[i].value;
                }
            }

            if (selectedCount === 0) {
                alert("请选择一条数据进行编辑");
            } else if (selectedCount > 1) {
                alert("只能同时编辑一条数据");
            } else {
                var url = "/edit_plist?filename=" + encodeURIComponent(selectedFilename);
                window.location.href = url;
            }
        }


        function batchDelete() {
            var table = document.getElementById("file-table");
            var checkboxes = table.querySelectorAll("input[type='checkbox']:checked");
            var filenames = [];

            for (var i = 0; i < checkboxes.length; i++) {
                var checkbox = checkboxes[i];
                var filename = checkbox.value;
                filenames.push(filename);
            }

            if (filenames.length === 0) {
                alert("请至少选择一个文件进行删除");
                return;
            }

            if (confirm("确定要删除选中的数据吗？")) {
                // 显示半透明黑色图层和旋转的圆圈
                var overlay = document.getElementById("overlay");
                var spinner = document.getElementById("spinner");
                overlay.style.display = "block";
                spinner.style.display = "block";

                // 发送批量删除请求...
                fetch("/batch_delete", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({ filenames: filenames })
                })
                .then(function(response) {
                    if (response.ok) {
                        // 批量删除成功，刷新页面
                        location.reload();
                    } else {
                        // 批量删除失败，显示错误信息
                        alert("批量删除失败");
                    }

                    // 隐藏半透明黑色图层和旋转的圆圈
                    overlay.style.display = "none";
                    spinner.style.display = "none";
                })
                .catch(function(error) {
                    console.log(error);
                    alert("批量删除失败");

                    // 隐藏半透明黑色图层和旋转的圆圈
                    overlay.style.display = "none";
                    spinner.style.display = "none";
                });
            }
        }
                                                                                 



    function closeBatchAddModal() {
        var modal = document.getElementById("batchAddModal");
        modal.style.display = "none";
        location.reload();
    }








function batchAdd() {
    var input = document.getElementById("batch-input");
    var links = input.value.trim().split('\n');
    var successCount = 0;
    var failureCount = 0;
    var incompleteCount = 0;
    var completedCount = 0;

    if (input.value === "") {
        alert("请输入至少一条链接");
        return;
    }

    if (links.length > 200) {
        var Count = links.length;
        alert("数量不能超过200条，你这有" + Count + "条");
        return;
    }

    // 显示半透明黑色图层和旋转的圆圈
    var overlay = document.getElementById("overlay");
    var spinner = document.getElementById("spinner");
    overlay.style.display = "block";
    spinner.style.display = "block";

    function uploadFile(link) {
        var filename = "";
        var enableValidation = true;  // 开关变量，控制是否开启链接格式验证功能


        if (enableValidation) {
            if (!link.startsWith("http") || !link.endsWith(".ipa")) {
            //    alert("链接格式不正确");

                incompleteCount++;
                checkCompletion();
            }
        }


        var url = "/ipa?url=" + encodeURIComponent(link) + "&filename=" + encodeURIComponent(filename);

        fetch(url)
            .then(function(response) {
                if (response.ok) {
                    return response.json();
                } else {
                    throw new Error("Network response was not ok");
                }
            })
            .then(function(data) {
                if (data.status === "success") {
                    successCount++;
                } else if (data.status === "duplicate") {
                    failureCount++;
                }
            })
            .catch(function(error) {
                console.log(error);
                failureCount++;
            })
            .finally(function() {
                completedCount++;
                checkCompletion();
            });
    }

    function checkCompletion() {
        if (completedCount === links.length) {
            var resultDiv = document.getElementById("batch-result");
            var message = "所有链接处理完毕\n";
            message += "成功上传：" + successCount + "条\n";
            message += "失败：" + failureCount + "条\n";
            message += "不合规链接：" + incompleteCount + "条";
            alert(message);
            location.reload();
        }
    }

    for (var i = 0; i < links.length; i++) {
        var link = links[i].trim();

        if (link !== "") {
            uploadFile(link);
        } else {
            incompleteCount++;
            checkCompletion();
        }
    }
}












        function clearBatchInput() {
            document.getElementById("batch-input").value = "";
        }

        function showBatchAddBox() {
            var modal = document.getElementById("batchAddModal");
            modal.style.display = "block";

            var span = document.getElementsByClassName("modal-close")[1];
            span.onclick = function() {
                modal.style.display = "none";
            }

            window.onclick = function(event) {
                if (event.target == modal) {
                    modal.style.display = "none";
                }
            }
        }

        function clearForm() {
            document.getElementById("link").value = "";
            document.getElementById("filename").value = "";
        }

        function showPromptBox() {
            var modal = document.getElementById("myModal");
            modal.style.display = "block";

            var span = document.getElementsByClassName("modal-close")[0];
            span.onclick = function() {
                modal.style.display = "none";
            }

            window.onclick = function(event) {
                if (event.target == modal) {
                    modal.style.display = "none";
                }
            }
        }

        function extractFilename() {
            var linkInput = document.getElementById("link");
            var filenameInput = document.getElementById("filename");
            var filenameHint = document.getElementById("filename-hint");
            var filenameLabel = document.querySelector("label[for='filename']");

            var link = linkInput.value.trim();
            var filename = "";

            var enableValidation = true;  // 开关变量，控制是否开启提示手写文件名功能

            if (link !== "") {
                var startIndex = link.lastIndexOf("/") + 1;
                filename = link.substring(startIndex);
                filename = decodeURIComponent(filename);  // 解码文件名

                if (enableValidation && (!link.startsWith("http") || !link.endsWith(".ipa"))) {
                    filename = "";
                }
            }

            filenameInput.value = filename;

            if (filename === "") {
                filenameHint.style.display = "block";
                filenameInput.required = true;
                filenameLabel.innerHTML = "请输入文件名称<span class='required-sign'>*</span>";
            } else {
                filenameHint.style.display = "none";
                filenameInput.required = false;
                filenameLabel.innerHTML = "请输入文件名称";
            }
        }


    function closeModal() {
        location.reload();
    }

    function submitForm() {
        var linkInput = document.getElementById("link");
        var filenameInput = document.getElementById("filename");

        var link = linkInput.value.trim();
        var filename = filenameInput.value.trim();

        var enableValidation = true;  // 开关变量，控制是否开启链接格式验证功能
        var allowEmptyFilename = false;  // 开关变量，控制是否允许空文件名

        if (enableValidation) {
            if (!link.startsWith("http") || !link.endsWith(".ipa")) {
                alert("链接格式不正确");
                return;
            }
        }

        if (!allowEmptyFilename && filename === "") {
            alert("文件名不能为空");
            return;
        }

        var url = "/ipa?url=" + encodeURIComponent(link) + "&filename=" + encodeURIComponent(filename);

        // 显示半透明黑色图层和旋转的圆圈
        var overlay = document.getElementById("overlay");
        var spinner = document.getElementById("spinner");
        overlay.style.display = "block";
        spinner.style.display = "block";

        fetch(url)
            .then(function(response) {
                if (response.ok) {
                    return response.json();
                } else {
                    throw new Error("Network response was not ok");
                }
            })
            .then(function(data) {
                if (data.status === "success") {
                    alert("上传成功");
                } else if (data.status === "duplicate") {
                    alert("链接重复");
                } else {
                    alert("上传失败");
                }
            })
            .catch(function(error) {
                console.log(error);
                alert("上传失败");
            })
            .finally(function() {
                // 隐藏半透明黑色图层和旋转的圆圈
                overlay.style.display = "none";
                spinner.style.display = "none";

                // 清空表单
                clearForm();

                // 关闭弹窗
                closeModal();
            });
    }


        function selectAll() {
            var checkboxes = document.getElementsByName("file-checkbox");

            for (var i = 0; i < checkboxes.length; i++) {
                checkboxes[i].checked = true;
            }

            var selectAllButton = document.getElementById("select-all-button");
            selectAllButton.innerHTML = "取消";
            selectAllButton.onclick = clearSelection;
        }

        function clearSelection() {
            var checkboxes = document.getElementsByName("file-checkbox");

            for (var i = 0; i < checkboxes.length; i++) {
                checkboxes[i].checked = false;
            }

            var selectAllButton = document.getElementById("select-all-button");
            selectAllButton.innerHTML = "全选";
            selectAllButton.onclick = selectAll;
        }

        function invertSelection() {
            var checkboxes = document.getElementsByName("file-checkbox");

            for (var i = 0; i < checkboxes.length; i++) {
                checkboxes[i].checked = !checkboxes[i].checked;
            }
        }
function syncData() {
    var xhr = new XMLHttpRequest();
    xhr.open('GET', '/sync', true);
    xhr.onreadystatechange = function() {
        if (xhr.readyState === 4) {
            if (xhr.status === 200) {
                // 数据同步成功
                alert('数据同步成功！');
            } else {
                // 数据同步失败
                alert('数据同步失败！');
            }
        }
    };
    xhr.onerror = function() {
        // 处理错误
        console.error('数据同步时发生错误');
        alert('数据同步时发生错误！');
    };
    xhr.send();
}

