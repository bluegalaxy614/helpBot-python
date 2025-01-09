function templateRender(template, obj) {
    return template.replace(/\${([^}]+)}/g, (match, path) => {
        return path.split('.').reduce((a,f) => a?a[f]:undefined, obj) ?? match
    });
}

class NginxUploadElement extends HTMLInputElement {
    constructor() {
        super();
    }

    isAcceptExtension(fileName) {
        const ext = fileName.split('.').pop();

        if (this.acceptExtensions.length === 0 || this.acceptExtensions.includes(`.${ext}`)) return true;

        return false;
    }

    getFileIcon(fileName) {
        const ext = fileName.split('.').pop();

        if (ext == 'pdf') return '<i class="bi bi-file-earmark-pdf"></i>';
        if (ext == 'txt') return '<i class="bi bi-file-earmark-text"></i>';
        if (ext == 'png') return '<i class="bi bi-file-earmark-image"></i>';
        if (ext == 'jpg') return '<i class="bi bi-file-earmark-image"></i>';
        if (ext == 'jpeg') return '<i class="bi bi-file-earmark-image"></i>';

        return '<i class="bi bi-file-earmark"></i>';
    }

    getFileSize(bytes) {
        if (bytes < 1e3) return `${bytes} bytes`;
        if (bytes < 1e6) return `${(bytes / 1e3).toFixed(1)} KB`;
        return `${(bytes / 1e6).toFixed(1)} MB`;
    }

    // getFileMtime(mtime) {
    //     let mTimeTs = Date.parse(mtime)
    //     return this.dateFormater.format(mTimeTs);
    // }

    connectedCallback() {
        this.uploadPath = this.getAttribute('upload-path');
        this.maxFiles = parseInt(this.getAttribute('max-files'));

        if (this.type !== "file") return;
        if (!this.uploadPath) return;

        this.fileNodes = new Map();
        this.acceptExtensions = this.accept.split(',').map(x => x.trim());
        this.dateFormater = new Intl.DateTimeFormat(
            document.documentElement.lang,
            {dateStyle: "medium", timeStyle: "medium"}
        );


        this.addEventListener("change", (e) => this.onChangeHandler(e));
        // this.form.addEventListener("submit", (e) => this.onSubmitHandler(e));

        setTimeout(() => this.onLoadHandler());
    }

    async onLoadHandler() {
        this.label = document.querySelector(`label[for=${this.id}]`);
        this.output = document.querySelector(`output[for=${this.id}]`);
        this.outputTemplate = ' \
            <input type="hidden" name="file" value="${file.path}"> \
            <strong>${file.icon} ${file.name}</strong> \
            <small><data value="${file.size_bytes}">${file.size}</data>, \
            <time datetime="${file.mtime_iso}">${file.mtime}</time></small>';

        if (this.output && this.output.querySelector('template')) {
            this.outputTemplate = this.output.querySelector('template').innerHTML;
        }

        await this.loadFileNodes();
        this.redrawOutput();
    }

    async onChangeHandler(event) {
        let totalBytes = 0;
        for (const file of this.files) totalBytes += file.size;

        const progress = document.createElement("progress");
        progress.value = 0;
        // progress.max = totalBytes / 1048576;
        progress.max = totalBytes;
        this.output.appendChild(progress);

        for (const file of this.files) {
            await new Promise(r => setTimeout(r, 500));
            progress.value += file.size;

            if (!this.fileNodes.has(file.name) && this.isAcceptExtension(file.name)) {
                let resp = await fetch(`${this.uploadPath}${file.name}`, {
                    method: "PUT",
                    body: file,
                });
                await new Promise(r => setTimeout(r, 500));
            }
        }

        await this.loadFileNodes();
        this.redrawOutput();
    }

    async deleteFile(filePath) {
        await fetch(filePath, {method: "DELETE"});
        await this.loadFileNodes();
        this.redrawOutput();
    }

    appendFileNode(fileRawData) {
        // [{
        //    "name": "Caderno de Algoritmos.pdf",
        //    "type": "file",
        //    "mtime": "Thu, 12 Sep 2024 04:56:27 GMT",
        //    "size": 196353
        // },...
        const node = document.createElement("div");

        const fileName = fileRawData['name'];
        const fileSize = fileRawData['size'];
        const fileMtime = new Date(Date.parse(fileRawData['mtime']));

        const data = {
            name: fileName,
            icon: this.getFileIcon(fileName),
            path: `${this.uploadPath}${fileName}`,
            size: this.getFileSize(fileSize),
            size_bytes: fileSize,
            mtime: this.dateFormater.format(fileMtime),
            mtime_iso: fileMtime.toISOString(),
        }

        node.innerHTML = templateRender(this.outputTemplate, {file: data});

        this.fileNodes.set(fileName, node);

        return node;
    }

    async loadFileNodes() {
        this.fileNodes.clear();

        let resp = await fetch(this.uploadPath, {method: "GET"});
        if (resp.status == 200) {
            let data = await resp.json();
            for (let info of data) {
                if (info.type == "file") {
                    this.appendFileNode(info);
                }
            }
        }
    }

    redrawOutput() {
        if (this.fileNodes.size === 0) return;

        this.output.innerHTML = '';
        for (let key of this.fileNodes.keys()) {
            let node = this.fileNodes.get(key);
            this.output.appendChild(node);
        }

        if (this.maxFiles && this.fileNodes.size > this.maxFiles) {
            this.disabled = 'on';
            if (this.label) this.label.className += ' disabled';
        }
    }

    // updateOutput() {
    //     if (!this.output) return;

    //     let html = '';
    //     this.files_map.forEach((file) => {
    //         html += `<div id="${file.name}">
    //         <strong>${file.name}</strong>
    //         <progress max="${file.size}" value="0"></progress>
    //         <span>${file.size}</span>
    //         <span>${file.type}</span></div>`;
    //     });
    //     this.output.innerHTML = html;
    // }

    // newItemNode(name, size, mtime, uploaded) {
    //     let item = document.createElement("div");
    //     let uplmark = (uploaded) ? '[*]' : '[-]';
    //     item.id = name;
    //     item.innerHTML = `<strong>${uplmark} ${name}</strong>
    //         <span>${size}</span>
    //         <span>${mtime}</span>`;

    //     if (this.output) this.output.appendChild(item);

    //     this.fileNodes.set(name, item);

    //     return item;
    // }
}

customElements.define("nginx-upload", NginxUploadElement, {extends: "input"});
