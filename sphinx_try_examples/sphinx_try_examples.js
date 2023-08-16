window.tryExamplesShowIframe = (examplesContainerId, iframeContainerId, iframeSrc) => {
    const examples_container = document.getElementById(examplesContainerId)
    const iframe_container = document.getElementById(iframeContainerId);
    const iframe = document.createElement('iframe');

    iframe.src = iframeSrc;
    iframe.width = iframe.height = '100%';
    iframe.classList.add('try_examples_raw_iframe');
    examples_container.classList.add("hidden")
    iframe_container.appendChild(iframe);
    iframe_container.classList.remove("hidden")
}
