<template>
  <div>
    <h1>模擬電商平台</h1>

    <!-- 上傳 Excel -->
    <div>
      <input type="file" @change="onFileChange" />
      <button @click="uploadExcel">上傳 Excel</button>
    </div>

    <!-- 篩選產品種類 -->
    <div v-if="categories.length" style="margin-top:20px;">
      <label>篩選產品種類:</label>
      <select v-model="selectedCategory" @change="filterProducts">
        <option value="">全部</option>
        <option v-for="(c, index) in categories" :key="index" :value="c">{{ c }}</option>
      </select>
    </div>

    <!-- 已上架商品 -->
    <div v-if="listedProducts.length" style="margin-top:20px;">
      <h2>已上架商品</h2>
      <table border="1">
        <thead>
          <tr>
            <th>產品種類</th>
            <th>產品名稱</th>
            <th>產品價格</th>
            <th>售賣商城</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(p, index) in listedProducts" :key="index">
            <td>{{ p.product_category }}</td>
            <td>
                <a :href="p.product_url" target="_blank" style="color: blue; text-decoration: underline;">
                    {{ p.product_name }}
                </a>
            </td>
            <td>{{ p.product_price }}</td>
            <td>{{ p.merchant_name }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 顯示上傳 Excel 結果 -->
    <div v-if="uploadResult" style="margin-top:20px;">
      <h2>上傳結果</h2>
      <p>檔案名稱: {{ uploadResult.filename }}</p>
      <p>資料筆數: {{ uploadResult.data_count }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const excelFile = ref(null)
const listedProducts = ref([])
const uploadResult = ref(null)
const selectedCategory = ref("")
const categories = ref([])  // 下拉選單的產品種類

// 選擇檔案
const onFileChange = (e) => {
  excelFile.value = e.target.files[0]
}

// 上傳 Excel
const uploadExcel = async () => {
  if (!excelFile.value) {
    alert('請先選擇 Excel 檔案')
    return
  }

  const formData = new FormData()
  formData.append('file', excelFile.value)

  try {
    const res = await fetch('http://localhost:8000/upload-excel/', {
      method: 'POST',
      body: formData
    })
    if (!res.ok) throw new Error('上傳失敗')
    const data = await res.json()

    // 將上傳結果顯示在前端
    uploadResult.value = data

    // 將資料加入已上架列表
    listedProducts.value = data.data.map(item => ({
      product_name: item["產品名稱"],
      product_category: item["產品種類"],
      product_price: item["產品價格"],
      product_url: item["產品網址"],
      merchant_name: item["售賣商城"]
    }))

    // 生成下拉選單選項 (去重)
    const set = new Set(listedProducts.value.map(p => p.product_category))
    categories.value = Array.from(set)

    alert('上傳成功')
  } catch (err) {
    console.error(err)
    alert('上傳失敗: ' + err.message)
  }
}

// 篩選函數 (呼叫後端 /query/)
const filterProducts = async () => {
  try {
    const res = await fetch(`http://localhost:8000/query/?category=${encodeURIComponent(selectedCategory.value)}`)
    if (!res.ok) throw new Error('篩選失敗')
    const data = await res.json()
    
    listedProducts.value = data.data.map(item => ({
      product_name: item["產品名稱"],
      product_category: item["產品種類"],
      product_price: item["產品價格"],
      product_url: item["產品網址"],
      merchant_name: item["售賣商城"]
    }))
  } catch (err) {
    console.error(err)
    alert('篩選失敗: ' + err.message)
  }
}
</script>
