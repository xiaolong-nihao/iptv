import json
import re
import os
import sys

def json_to_m3u(json_file_path, m3u_file_path):
    """
    将JSON文件转换为M3U文件
    """
    try:
        # 读取JSON文件
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 写入M3U文件
        with open(m3u_file_path, 'w', encoding='utf-8') as f:
            f.write('#EXTM3U\n')
            
            # 查找频道数据
            channels = []
            if isinstance(data, list):
                channels = data
            elif 'data' in data and isinstance(data['data'], list):
                channels = data['data']
            elif 'channels' in data and isinstance(data['channels'], list):
                channels = data['channels']
            else:
                # 尝试找到任何包含频道数据的列表
                for key, value in data.items():
                    if isinstance(value, list) and value and isinstance(value[0], dict):
                        channels = value
                        break
            
            if not channels:
                print("错误: 无法找到频道数据")
                return False
                
            valid_channels = 0
            for channel in channels:
                # 尝试不同的字段名来获取频道信息
                name = channel.get('name') or channel.get('channelName') or channel.get('title') or '未知频道'
                url = channel.get('url') or channel.get('urls') or channel.get('streamUrl') or channel.get('source') or ''
                group = channel.get('group') or channel.get('category') or channel.get('type') or '其他'
                logo = channel.get('logo') or channel.get('icon') or channel.get('image') or ''
                
                # 如果URL是列表，取第一个
                if isinstance(url, list):
                    url = url[0] if url else ''
                
                # 清理名称中的特殊字符
                name = re.sub(r'[^\w\s-]', '', str(name))
                group = re.sub(r'[^\w\s-]', '', str(group))
                
                if url and url.startswith(('http://', 'https://', 'rtmp://', 'rtsp://')):
                    # 写入EXTINF信息
                    extinf_line = f'#EXTINF:-1'
                    
                    # 添加可选属性
                    if logo:
                        extinf_line += f' tvg-logo="{logo}"'
                    
                    extinf_line += f' group-title="{group}",{name}\n'
                    
                    f.write(extinf_line)
                    f.write(url + '\n')
                    valid_channels += 1
            
            print(f"成功处理 {valid_channels}/{len(channels)} 个频道")
            return True
            
    except FileNotFoundError:
        print(f"错误: 找不到文件 {json_file_path}")
        return False
    except json.JSONDecodeError as e:
        print(f"错误: JSON文件格式不正确 - {str(e)}")
        return False
    except Exception as e:
        print(f"处理过程中发生错误: {str(e)}")
        return False

if __name__ == "__main__":
    # 设置文件路径 - 专用目录版本
    # JSON文件在当前目录 (m3u-generator/)
    json_file = 'getAllChannel.json'
    # M3U文件输出到上级目录 (仓库根目录)
    m3u_file = '../tv.m3u'
    
    # 检查JSON文件是否存在
    if not os.path.exists(json_file):
        print(f"错误: 文件 {json_file} 不存在")
        print("当前工作目录:", os.getcwd())
        print("目录内容:")
        for file in os.listdir('.'):
            print(f"  - {file}")
        sys.exit(1)
    
    # 执行转换
    success = json_to_m3u(json_file, m3u_file)
    
    if success:
        print(f"✅ M3U文件已生成: {m3u_file}")
        # 检查文件是否生成成功
        if os.path.exists(m3u_file):
            file_size = os.path.getsize(m3u_file)
            line_count = sum(1 for _ in open(m3u_file, 'r', encoding='utf-8'))
            print(f"📁 文件大小: {file_size} 字节")
            print(f"📊 文件行数: {line_count} 行")
        else:
            print("⚠️  警告: M3U文件未找到，可能生成失败")
    else:
        print("❌ 转换失败")
        sys.exit(1)
