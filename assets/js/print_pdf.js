function createPDF(){
    console.log("Starting PDF creation...");
    
    const printArea = document.getElementById("mainContainer");
    
    if (!printArea) {
        console.error("Element with id 'mainContainer' not found");
        alert("Không tìm thấy nội dung để tạo PDF!");
        return;
    }
    
    if (typeof html2canvas === 'undefined') {
        console.error("html2canvas library not loaded");
        alert("Thư viện html2canvas chưa được tải!");
        return;
    }
    
    if (typeof jsPDF === 'undefined') {
        console.error("jsPDF library not loaded");
        alert("Thư viện jsPDF chưa được tải!");
        return;
    }
    
    console.log("Libraries loaded, creating PDF...");
    
    // Use callback approach for older html2canvas versions
html2canvas(printArea, {
    scale: 2,
    useCORS: true,
    backgroundColor: '#000000'
}).then(function(canvas) {
    console.log("Canvas created, generating PDF...");

    var imgData = canvas.toDataURL('image/png');
    var doc = new jsPDF('p', 'mm', "a4");

    const pageHeight = doc.internal.pageSize.getHeight();
    const imgWidth = doc.internal.pageSize.getWidth();
    var imgHeight = canvas.height * imgWidth / canvas.width;
    var heightLeft = imgHeight;

    var position = 0; // top padding for first page

    doc.addImage(imgData, 'PNG', 0, position, imgWidth, imgHeight);
    heightLeft -= pageHeight;

    while (heightLeft > 0) {
        position = heightLeft - imgHeight + 10; 
        doc.addPage();
        doc.addImage(imgData, 'PNG', 0, position, imgWidth, imgHeight);
        heightLeft -= pageHeight;
    }

    console.log("PDF created, saving...");
    doc.save('IMDB_Dashboard.pdf');
    console.log("PDF saved successfully!");
});

}

// Wait for DOM to be ready and add event listener
document.addEventListener('DOMContentLoaded', function() {
    console.log("DOM loaded, setting up PDF button...");
    
    // Wait a bit more for all scripts to load
    setTimeout(function() {
        try {
            const pdfButton = document.getElementById("run");
            if (pdfButton) {
                pdfButton.addEventListener("click", function(){
                    console.log("PDF button clicked!");
                    createPDF();
                });
                console.log('PDF button listener added successfully!');
            } else {
                console.error("PDF button with id 'run' not found");
            }
        }
        catch(err) {
            console.error("Error setting up PDF button:", err);
        }
    }, 1000);
});
