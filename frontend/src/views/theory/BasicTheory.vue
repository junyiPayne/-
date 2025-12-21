<template>
  <div class="basic-theory">
    <el-card class="box-card">
      <template #header>
        <div class="card-header">
          <span>基础理论参考</span>
        </div>
      </template>
      
      <el-collapse v-model="activeNames">
        <!-- 附件 1 -->
        <el-collapse-item title="附件 1. 根据 BMI 划分的普通成年人的体重等级" name="1">
          <el-table :data="bmiData" border style="width: 100%">
            <el-table-column prop="range" label="BMI 范围" />
            <el-table-column prop="status" label="体重等级" />
          </el-table>
          <div class="source">来源：王卫庆,万沁,马建华,等.中国成人体重管理指南[J].中华内分泌代谢杂志,2025,41(11):891-907.</div>
        </el-collapse-item>

        <!-- 附件 2 -->
        <el-collapse-item title="附件 2. 根据体脂率划分的普通成年人的身体成分等级" name="2">
          <el-table :data="bodyFatData" border style="width: 100%">
            <el-table-column prop="male" label="体脂率范围 (男性)" />
            <el-table-column prop="female" label="体脂率范围 (女性)" />
            <el-table-column prop="status" label="体重等级" />
          </el-table>
          <div class="source">来源：王卫庆,万沁,马建华,等.中国成人体重管理指南[J].中华内分泌代谢杂志,2025,41(11):891-907.</div>
        </el-collapse-item>

        <!-- 附件 3 -->
        <el-collapse-item title="附件 3. 根据体脂率划分的普通成年人的体重等级 (详细)" name="3">
          <el-table :data="bodyFatAgeData" border style="width: 100%" :span-method="objectSpanMethod">
            <el-table-column prop="gender" label="性别" width="80" />
            <el-table-column prop="age" label="年龄" width="100" />
            <el-table-column prop="low" label="体脂过少" />
            <el-table-column prop="excellent" label="非常好" />
            <el-table-column prop="good" label="很好" />
            <el-table-column prop="normal" label="正常" />
            <el-table-column prop="high" label="体脂多" />
            <el-table-column prop="veryHigh" label="体脂过多" />
          </el-table>
          <div class="source">来源：第四版《运动生理学》教材，高等教育出版社</div>
        </el-collapse-item>

        <!-- 附件 4 -->
        <el-collapse-item title="附件 4. 根据腰围划分的普通成年人的肥胖临界点" name="4">
          <el-table :data="waistData" border style="width: 100%">
            <el-table-column prop="male" label="腰围范围 (男性)" />
            <el-table-column prop="female" label="腰围范围 (女性)" />
            <el-table-column prop="status" label="体重等级" />
          </el-table>
          <div class="source">来源：王卫庆,万沁,马建华,等.中国成人体重管理指南[J].中华内分泌代谢杂志,2025,41(11):891-907.</div>
        </el-collapse-item>

        <!-- 附件 5 -->
        <el-collapse-item title="附件 5. 根据腰臀比划分的普通成年人的中心性肥胖临界点" name="5">
          <el-table :data="whrData" border style="width: 100%">
            <el-table-column prop="male" label="腰臀比范围 (男性)" />
            <el-table-column prop="female" label="腰臀比范围 (女性)" />
            <el-table-column prop="status" label="体重等级" />
          </el-table>
          <div class="source">来源：王卫庆,万沁,马建华,等.中国成人体重管理指南[J].中华内分泌代谢杂志,2025,41(11):891-907.</div>
        </el-collapse-item>

        <!-- 附件 6 -->
        <el-collapse-item title="附件 6. 根据腰高比划分的普通成年人的内脏脂肪临界点" name="6">
          <el-table :data="whtrData" border style="width: 100%">
            <el-table-column prop="range" label="腰高比范围" />
            <el-table-column prop="status" label="临界点" />
          </el-table>
          <div class="source">来源：王卫庆,万沁,马建华,等.中国成人体重管理指南[J].中华内分泌代谢杂志,2025,41(11):891-907.</div>
        </el-collapse-item>

      </el-collapse>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const activeNames = ref(['1', '2', '3', '4', '5', '6'])

const bmiData = [
  { range: '<18.5 kg/m²', status: '偏瘦' },
  { range: '18.5~23.9 kg/m²', status: '正常' },
  { range: '24.0~27.9 kg/m²', status: '超重' },
  { range: '>28.0 kg/m²', status: '肥胖' },
]

const bodyFatData = [
  { male: '10%~20%', female: '15%~25%', status: '正常' },
  { male: '>25%', female: '>30%', status: '肥胖' },
]

const waistData = [
  { male: '≥90 cm', female: '≥85 cm', status: '肥胖' },
]

const whrData = [
  { male: '≥0.90', female: '≥0.85', status: '中心性肥胖' },
]

const whtrData = [
  { range: '≥0.5', status: '内脏脂肪超标' },
]

const bodyFatAgeData = [
  // 男性
  { gender: '男性', age: '≤19', low: '<3', excellent: '12', good: '12.1~17', normal: '17.1~22', high: '22.1~27', veryHigh: '≥27.1' },
  { gender: '男性', age: '20~29', low: '<3', excellent: '13', good: '13.1~18', normal: '18.1~23', high: '23.1~28', veryHigh: '≥28.1' },
  { gender: '男性', age: '30~39', low: '<3', excellent: '14', good: '14.1~19', normal: '19.1~24', high: '24.1~29', veryHigh: '≥29.1' },
  { gender: '男性', age: '40~49', low: '<3', excellent: '15', good: '15.1~20', normal: '20.1~25', high: '25.1~30', veryHigh: '≥30.1' },
  { gender: '男性', age: '≥50', low: '<3', excellent: '16', good: '16.1~21', normal: '21.1~26', high: '26.1~31', veryHigh: '≥31.1' },
  // 女性
  { gender: '女性', age: '≤19', low: '<12', excellent: '17', good: '17.1~22', normal: '22.1~27', high: '27.1~32', veryHigh: '≥32.1' },
  { gender: '女性', age: '20~29', low: '<12', excellent: '18', good: '18.1~23', normal: '23.1~28', high: '28.1~33', veryHigh: '≥33.1' },
  { gender: '女性', age: '30~39', low: '<12', excellent: '19', good: '19.1~24', normal: '24.1~29', high: '29.1~34', veryHigh: '≥34.1' },
  { gender: '女性', age: '40~49', low: '<12', excellent: '20', good: '20.1~25', normal: '25.1~30', high: '39.1~35', veryHigh: '≥35.1' },
  { gender: '女性', age: '≥50', low: '<12', excellent: '21', good: '21.1~26', normal: '26.1~31', high: '31.1~36', veryHigh: '≥36.1' },
]

const objectSpanMethod = ({ row, column, rowIndex, columnIndex }) => {
  if (columnIndex === 0) {
    if (rowIndex === 0) {
      return { rowspan: 5, colspan: 1 }
    } else if (rowIndex === 5) {
      return { rowspan: 5, colspan: 1 }
    } else {
      return { rowspan: 0, colspan: 0 }
    }
  }
}
</script>

<style scoped>
.basic-theory {
  padding: 20px;
}
.source {
  margin-top: 10px;
  font-size: 12px;
  color: #909399;
  font-style: italic;
}
</style>