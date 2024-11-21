<template>
    <VuePdfEmbed 
        annotation-layer 
        text-layer 
        :source="BUCKET_URL + currentFile.rfileInOSS" 
    />
</template>

<script setup>
import { ref } from 'vue';
import { useRoute } from 'vue-router';
import VuePdfEmbed from 'vue-pdf-embed';
import { fileSearchService } from '@/api/homepage';

const route = useRoute();
const currentFile = ref({});
const courseNo = route.params.courseNo;
const rno = route.params.rno;
const BUCKET_URL = 'https://edu-platform-2024.oss-cn-beijing.aliyuncs.com/';

const fetchFile = async () => {
    try{
        let result = await fileSearchService(courseNo,rno);
        if(result.status === 200){
            currentFile.value = result.data.data;
        }
    } catch (err) {
        console.log(err);
    }
};

fetchFile();
</script>