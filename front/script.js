document.addEventListener("DOMContentLoaded", () => {
    // 載入所有醫院資料
    fetchAndRenderData();
    
    // 選擇特定醫院的按鈕
    document.getElementById("hospitalSelect").addEventListener("change", (event) => {
        const hospitalKey = event.target.value;
        if (hospitalKey === "all") {
            fetchAndRenderData(); // 顯示所有醫院
        } else {
            fetchSingleHospitalData(hospitalKey); // 顯示特定醫院
        }
    });
});

function fetchAndRenderData() {
    fetch("API_URL")
        .then(response => response.json())
        .then(data => {
            renderHospitalTables(data);
        })
        .catch(error => {
            console.error("Error fetching data:", error);
            document.getElementById("hospitalContainer").innerHTML = "無法取得資料";
        });
}

function fetchSingleHospitalData(hospitalKey) {
    fetch(`API_URL/${hospitalKey}`)
        .then(response => response.json())
        .then(data => {
            renderHospitalTables({ [hospitalKey]: data });
        })
        .catch(error => {
            console.error("Error fetching single hospital data:", error);
            document.getElementById("hospitalContainer").innerHTML = "無法取得資料";
        });
}

function renderHospitalTables(data) {
    const hospitalNames = {
        "chimei_main": "奇美醫院",
        "chimei_liuying": "柳營奇美醫院",
        "chimei_jiali": "佳里奇美醫院",
        "kuo": "郭綜合醫院",
        "annan": "安南醫院",
        "tainan": "台南醫院",
        "nckuh": "成大醫院",
        "sinlau_tainan": "台南新樓醫院",
        "sinlau_madou": "麻豆新樓醫院"
    };

    const container = document.getElementById("hospitalContainer");
    container.innerHTML = ""; 

    for (const hospitalKey in data) {
        if (data.hasOwnProperty(hospitalKey)) {
            const hospitalData = data[hospitalKey];
            const hospitalName = hospitalNames[hospitalKey] || hospitalKey;

            const hospitalSection = document.createElement("div");
            hospitalSection.classList.add("hospital-table");

            const title = document.createElement("h3");
            title.innerText = hospitalName;
            hospitalSection.appendChild(title);

            const table = document.createElement("table");
            const thead = document.createElement("thead");
            const headerRow = document.createElement("tr");

            ["病床類別", "總床數", "佔床數", "空床數", "佔床率"].forEach(headerText => {
                const th = document.createElement("th");
                th.innerText = headerText;
                headerRow.appendChild(th);
            });

            thead.appendChild(headerRow);
            table.appendChild(thead);

            const tbody = document.createElement("tbody");

            hospitalData.forEach(bedInfo => {
                const row = document.createElement("tr");
                ["病床類別", "總床數", "佔床數", "空床數", "佔床率"].forEach(key => {
                    const td = document.createElement("td");
                    td.innerText = bedInfo[key];
                    row.appendChild(td);
                });
                tbody.appendChild(row);
            });

            table.appendChild(tbody);
            hospitalSection.appendChild(table);
            container.appendChild(hospitalSection);
        }
    }
}
