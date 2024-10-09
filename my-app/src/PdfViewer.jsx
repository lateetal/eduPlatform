import React, { useEffect, useState, useRef } from 'react';
import { Spin, Tooltip, Input } from 'antd';
import { LeftOutlined, RightOutlined, ZoomInOutlined, ZoomOutOutlined } from '@ant-design/icons';

import { Document, Page, pdfjs } from "react-pdf";
import 'react-pdf/dist/esm/Page/AnnotationLayer.css';
import 'react-pdf/dist/esm/Page/TextLayer.css';
pdfjs.GlobalWorkerOptions.workerSrc = `//unpkg.com/pdfjs-dist@${pdfjs.version}/build/pdf.worker.min.js`;

const PageCom = (props) => {
  const [filePath, setFilePath] = useState(null);

  const [pageCurrent, setPageCurrent] = useState(1);
  const pageCurrentRef = useRef(pageCurrent);

  const [pageTotal, setPageTotal] = useState(1);
  const pageTotalRef = useRef(pageTotal);

  const [pageWidth, setPageWidth] = useState(960);
  const pageWidthRef = useRef(pageWidth);

  useEffect(()=>{
    setPageCurrent(1);
    pageCurrentRef.current= 1;

    setFilePath(props.filePath);
  },[props.filePath])

  const prevPage = () => {
    if (pageCurrentRef.current == 1) { return; }
    setPageCurrent(pageCurrentRef.current - 1);
    pageCurrentRef.current= pageCurrentRef.current - 1;
  };

  const nextPage = () => {
    if (pageCurrentRef.current == pageTotalRef.current) {
      return;
    }

    setPageCurrent(pageCurrentRef.current + 1);
    pageCurrentRef.current= pageCurrentRef.current + 1;
  };

  const pageNumChange = e => {
    let value = Number(e.target.value);
    let value2 = 1;

    if(value<=0){
        value2 = 1;
    } else if(value >= pageTotalRef.current){
        value2 = pageTotalRef.current;
    } else {
        value2 = value;
    }

    setPageCurrent(value);
    pageCurrentRef.current= value;
  };

  const toPage = e => {
    console.log('toPage====',e)
    let value = Number(e.target.value);
    let value2 = value;

    if(value<=0){
        value2 = 1;
    } else if(value >= pageTotalRef.current){
        value2 = pageTotalRef.current;
    } else {
        value2 = value;
    }
    setPageCurrent(value2);
    pageCurrentRef.current= value2;
  };

  const pageZoomOut = () => {
    if (pageWidthRef.current <= 960) {
      return
    }
    const pageWidth = pageWidthRef.current * 0.8;
    setPageWidth(pageWidth);
    pageWidthRef.current = pageWidth;
  };

  const pageZoomIn = () => {
    const pageWidth = pageWidthRef.current * 1.2
    setPageWidth(pageWidth);
    pageWidthRef.current = pageWidth;
  };

  const onDocumentLoadSuccess = (args) => {
    setPageTotal(args.numPages);
    pageTotalRef.current = args.numPages;
  };

  return (
    <div className="pdfViewer-wrapper">
      {filePath?(<>
        <div className="pageContainer">
          <Document file={filePath} onLoadSuccess={ onDocumentLoadSuccess }  loading={<Spin size="large" />} >
            <Page pageNumber={pageCurrent} width={pageWidth} loading={<Spin size="large" />}  />
          </Document>
        </div>

        <div className="pageTool">
          <Tooltip title={pageCurrent == 1 ? "已是第一页" : "上一页"}>
            <LeftOutlined onClick={prevPage} />
          </Tooltip>
          <Input value={pageCurrent} onChange={ pageNumChange } onPressEnter={ toPage } type="number" /> / {pageTotal}
          <Tooltip title={pageCurrent == pageTotal ? "已是最后一页" : "下一页"}>
            <RightOutlined onClick={ nextPage } />
          </Tooltip>
          <Tooltip title="放大">
            <ZoomInOutlined onClick={ pageZoomIn } />
          </Tooltip>
          <Tooltip title="缩小">
            <ZoomOutOutlined onClick={ pageZoomOut } />
          </Tooltip>
        </div>
      </>):(<div className="empty-wrapper">未生成报告文件！</div>)}
    </div>
  );
};

export default PageCom;