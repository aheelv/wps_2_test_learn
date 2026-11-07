理论题库（离线单文件刷题应用）
================================
本目录由 tools/site_theory.py 生成，请勿手工编辑 index.html。
  源文件：11-6/index.html（由 11-6/build/make_page.py 注入题库生成）
  题库数据：11-6/quiz_data.json（2 分册 / 781 题）
  栏目主页：../理论考试.html
  配置来源：tools/site_config.json
生成动作：替换页面标题 + 插入与主站一致的「站点导航」条；应用本体不外链任何资源，
          可整页离线使用，进度保存在浏览器 localStorage。
重建顺序：python 11-6/build/make_page.py → python tools/site_theory.py → python tools/site_nav.py
