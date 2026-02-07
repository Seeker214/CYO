import numpy as np

def analyze_histogram(image):
    """
    计算图像直方图数据。
    
    Args:
        image: numpy array, 形状为 (H, W) 或 (H, W, C)
        
    Returns:
        dict: 包含不同通道的直方图数据，格式为 {'channel_name': counts_array}
    """
    img_arr = np.array(image)
    
    hist_data = {}
    
    # 判断是灰度图还是彩色图
    if len(img_arr.shape) == 2:
        # 灰度图
        hist, _ = np.histogram(img_arr.flatten(), bins=256, range=[0, 256])
        hist_data['Gray'] = hist.tolist()
    else:
        # 彩色图 (假设是 RGB 或 BGR)
        # 如果是 opencv 读取的图片通常是 BGR，PIL 读取的是 RGB
        # 这里通用处理，按通道顺序命名 Channel 0, 1, 2
        channels = img_arr.shape[2]
        colors = ['Blue', 'Green', 'Red'] if channels == 3 else [f'Ch{i}' for i in range(channels)]
        
        for i in range(channels):
            hist, _ = np.histogram(img_arr[:, :, i].flatten(), bins=256, range=[0, 256])
            hist_data[colors[i] if i < 3 else f'Ch{i}'] = hist.tolist()
            
    return hist_data

def analyze_information_entropy(image):
    """
    计算图像的信息熵 (Information Entropy)。
    公式: H = - sum(p(x) * log2(p(x)))
    
    Args:
        image: numpy array
        
    Returns:
        float: 信息熵值
    """
    img_arr = np.array(image)
    
    flat_img = img_arr.flatten()
    
    counts = np.bincount(flat_img, minlength=256)
    
    probs = counts / len(flat_img)
    
    probs = probs[probs > 0]
    
    entropy = -np.sum(probs * np.log2(probs))
    
    return float(entropy)

def analyze_pixel_corelation(image, sample_size=3000):
    """
    分析相邻像素的相关性（水平、垂直、对角线）。
    由于全图计算量大且散点图密集，通常随机采样 N 个点进行分析。
    
    Args:
        image: numpy array
        sample_size: int, 用于散点图和计算的采样点数量
        
    Returns:
        dict: 包含三个方向的 相关系数(coefficient) 和 散点数据(plot_data)
    """
    img_arr = np.array(image)
    
    if len(img_arr.shape) == 3:
        if img_arr.shape[2] == 3:
            img_gray = np.dot(img_arr[...,:3], [0.299, 0.587, 0.114]).astype(np.uint8)
        else:
            img_gray = img_arr[:, :, 0] # 取第一个通道兜底
    else:
        img_gray = img_arr

    H, W = img_gray.shape
    num_pixels = H * W
    
    if num_pixels < sample_size:
        sample_size = num_pixels
        
    # 生成随机坐标 (y, x)
    # 范围限制在 [0, H-2] 和 [0, W-2] 以确保 (x+1, y+1) 存在
    rand_y = np.random.randint(0, H - 1, sample_size)
    rand_x = np.random.randint(0, W - 1, sample_size)
    
    results = {}
    
    directions = {
        'Horizontal': (0, 1),  # (y, x) vs (y, x+1)
        'Vertical':   (1, 0),  # (y, x) vs (y+1, x)
        'Diagonal':   (1, 1)   # (y, x) vs (y+1, x+1)
    }
    
    base_pixels = img_gray[rand_y, rand_x] # 原始点像素值
    
    for name, (dy, dx) in directions.items():
        # 获取相邻点像素值
        neighbor_pixels = img_gray[rand_y + dy, rand_x + dx]
        
        # 计算皮尔逊相关系数
        # np.corrcoef 返回矩阵 [[1, r], [r, 1]]，我们需要 r
        if np.std(base_pixels) == 0 or np.std(neighbor_pixels) == 0:
             correlation = 0.0 # 避免除以零
        else:
            correlation = np.corrcoef(base_pixels, neighbor_pixels)[0, 1]
        
        results[name] = {
            'correlation_coefficient': float(correlation),
            'plot_data': {
                'x': base_pixels.tolist(),      # 前端散点图 X 轴数据
                'y': neighbor_pixels.tolist()   # 前端散点图 Y 轴数据
            }
        }
        
    return results


def calculate_npcr_uaci(img1, img2):
    """
    计算两个图像之间的 NPCR 和 UACI 指标
    
    NPCR (Number of Pixels Change Rate): 像素变化率
    - 理想值接近 99.6094% (8位图像)
    
    UACI (Unified Average Changing Intensity): 平均变化强度  
    - 理想值接近 33.4635% (8位图像)
    
    Args:
        img1: 第一个图像 (numpy array)
        img2: 第二个图像 (numpy array)
        
    Returns:
        tuple: (npcr, uaci) 两个百分比值
    """
    if img1.shape != img2.shape:
        raise ValueError("两个图像尺寸必须相同")
    
    # 转换为整型数组避免浮点运算误差
    img1 = img1.astype(np.int32)
    img2 = img2.astype(np.int32)
    
    # 计算总像素数（包括所有通道）
    total_pixels = img1.size
    
    # NPCR: 统计不同的像素数量
    diff_pixels = np.sum(img1 != img2)
    npcr = (diff_pixels / total_pixels) * 100.0
    
    # UACI: 计算平均变化强度
    abs_diff = np.abs(img1 - img2)
    uaci = (np.sum(abs_diff) / (total_pixels * 255.0)) * 100.0
    
    return npcr, uaci