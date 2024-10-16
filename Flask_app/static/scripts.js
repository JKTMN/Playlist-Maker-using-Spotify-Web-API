function loginToSpotify() {
    alert("Logging into Spotify...");
    // Add your actual Spotify login logic here.
}

const blobSVGs = [
    `<svg viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg">
        <path fill="#117019" d="M34.9,-47.3C43.8,-34.1,48.6,-21.8,46.9,-11.3C45.2,-0.8,36.9,7.9,32.1,20.9C27.4,33.9,26.2,51.2,16.7,61.5C7.2,71.8,-10.6,74.9,-20,66.5C-29.3,58,-30.1,38,-29,24.3C-27.8,10.7,-24.7,3.4,-24.3,-5.3C-24,-14,-26.5,-24.3,-22.9,-38.5C-19.3,-52.7,-9.7,-70.8,1.7,-72.8C13,-74.7,26,-60.6,34.9,-47.3Z" transform="translate(100 100)" />
    </svg>`,
    `<svg viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg">
        <path fill="#117019" d="M37,-53.9C48.1,-42.8,57.5,-32.3,54.2,-22.4C50.9,-12.5,34.9,-3.2,30.1,9.3C25.4,21.7,31.9,37.3,28.8,51.6C25.6,65.9,12.8,78.9,0.3,78.5C-12.2,78.1,-24.4,64.3,-34.5,52.2C-44.6,40.2,-52.6,29.9,-54.8,18.8C-57,7.7,-53.5,-4.3,-45.1,-9.9C-36.8,-15.5,-23.5,-14.8,-15.2,-26.8C-6.8,-38.9,-3.4,-63.6,4.7,-70.1C12.9,-76.7,25.8,-65,37,-53.9Z" transform="translate(100 100)" />
    </svg>`,
    `<svg viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg">
        <path fill="#117019" d="M38.1,-58.8C42.3,-49.4,33.6,-28.8,27.3,-16.4C20.9,-4,16.9,0.1,16,5.8C15,11.5,17,18.8,14.8,32C12.7,45.2,6.3,64.1,0.9,62.9C-4.5,61.6,-9,40,-20.8,30C-32.7,20,-51.9,21.6,-54.4,16.9C-57,12.3,-42.8,1.5,-40.7,-15.7C-38.5,-32.9,-48.3,-56.5,-43.5,-65.6C-38.8,-74.7,-19.4,-69.4,-1.2,-67.7C17,-66,34,-68.1,38.1,-58.8Z" transform="translate(100 100)" />
    </svg>`
];

const blobsCount = 20;
const bodyWidth = document.body.clientWidth;
const bodyHeight = document.body.clientHeight;
const existingBlobs = [];

function generateRandomBlob() {
    const randomSVG = blobSVGs[Math.floor(Math.random() * blobSVGs.length)];

    const blob = document.createElement('div');
    blob.classList.add('random-blob');
    blob.innerHTML = randomSVG;

    const size = Math.random() * 300 + 50;
    const rotation = Math.random() * 360;
    const opacity = Math.random() * (0.9 - 0.2) + 0.2;

    let xPos, yPos;
    let tries = 0;
    do {
        xPos = Math.random() * (bodyWidth - size);
        yPos = Math.random() * (bodyHeight - size);
        tries++;
    } while (checkOverlap(xPos, yPos, size) && tries < 100);

    blob.style.position = 'absolute';  // Ensure absolute positioning
    blob.style.width = `${size}px`;
    blob.style.height = `${size}px`;
    blob.style.transform = `rotate(${rotation}deg)`;
    blob.style.opacity = opacity;
    blob.style.top = `${yPos}px`;
    blob.style.left = `${xPos}px`;
    blob.style.zIndex = '-1';  // Place blobs behind other elements
    blob.style.pointerEvents = 'none';  // Prevent interaction

    document.body.appendChild(blob);
    existingBlobs.push({xPos, yPos, size});
}


function checkOverlap(xPos, yPos, size) {
    return existingBlobs.some(blob => {
        const distance = Math.hypot(blob.xPos - xPos, blob.yPos - yPos);
        return distance < (blob.size + size) / 2;
    });
}

for (let i = 0; i < blobsCount; i++) {
    generateRandomBlob();
}
