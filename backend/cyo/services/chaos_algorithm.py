import numpy as np
from cyo.utils.chaos import get_R_matrix

def encryption(image, key):
    """
    encrypt the image
    
    :param image: the image will be encrypted, format: numpy
    :param key: 密钥
    """
    if not isinstance(image, np.ndarray):
        image = np.array(image)
        
    # 转换为 float64 进行计算，防止 mod 256 之前的溢出
    img_data = image.copy().astype(np.float64)
    M, W, _ = img_data.shape
    Sum = M * W
    
    p1_val, q1_val = key.split(",")
    p1_val, q1_val = np.float32(p1_val), np.float32(q1_val)
    
    # 混沌矩阵生成 (需确保 get_R_matrix 内部 reshape 使用 order='F')
    RR, RG, RB, p, q = get_R_matrix(W, M, p1_val, q1_val)
    t = np.gcd(M, W)
    Min_val = min(M, W)

    I1 = img_data[:, :, 0]
    I2 = img_data[:, :, 1]
    I3 = img_data[:, :, 2]

    # --- 1. 十字交叉置换 (Scrambling) ---
    for i in range(0, M, t):
        for j in range(0, W, t):
            # MATLAB 索引从 1 开始，这里对应 0-based
            # 确保索引不会越界
            wi = min(int(np.floor(RR[i, j] * M)), M - 1)
            wj = min(int(np.floor(RG[i, j] * W)), W - 1)
            wy = min(int(np.floor(RB[i, j] * Min_val)), Min_val - 1)

            # 行变换：跨通道循环位移 (I1 -> I2 -> I3 -> I1)
            # 模拟 MATLAB: TH = [I3_tail, I1, I2, I3_head]
            row_combined = np.concatenate([I1[wi, :], I2[wi, :], I3[wi, :]])
            row_rolled = np.roll(row_combined, wy) # 向右滚动 wy
            I1[wi, :] = row_rolled[0:W]
            I2[wi, :] = row_rolled[W:2*W]
            I3[wi, :] = row_rolled[2*W:3*W]

            # 列变换：跨通道循环位移
            col_combined = np.concatenate([I1[:, wj], I2[:, wj], I3[:, wj]])
            col_rolled = np.roll(col_combined, wy) # 向下滚动 wy
            I1[:, wj] = col_rolled[0:M]
            I2[:, wj] = col_rolled[M:2*M]
            I3[:, wj] = col_rolled[2*M:3*M]

    # --- 2. 混淆扩散 (Diffusion) ---
    # MATLAB: A = [I1(:) I2(:) I3(:)]'; A = A(:)';
    # 构造 [R1, G1, B1, R2, G2, B2...] 交替序列
    f1 = I1.flatten(order='F')
    f2 = I2.flatten(order='F')
    f3 = I3.flatten(order='F')
    A = np.vstack((f1, f2, f3)).flatten(order='F')

    total_len = 3 * Sum
    B = np.zeros(total_len)
    C = np.zeros(total_len)
    S1 = np.floor(256 * (p + q) / 2).flatten()
    S2 = np.floor(256 * p).flatten()

    # 逆向扩散 (Backward Diffusion)
    B[total_len-1] = (A[total_len-1] + S1[total_len-1]) % 256
    for i in range(total_len - 2, -1, -1):
        B[i] = (B[i+1] + S1[i] + A[i]) % 256

    # 正向扩散 (Forward Diffusion)
    C[0] = (B[0] + S2[0]) % 256
    for i in range(1, total_len):
        C[i] = (C[i-1] + B[i] + S2[i]) % 256

    # --- 3. 还原图像 (Reshape) ---
    # MATLAB: I1 = reshape(C(1:M*W), M, W)
    # 重点：此处使用顺次截取
    I1_new = C[0:Sum].reshape((M, W), order='F').astype(np.uint8)
    I2_new = C[Sum:2*Sum].reshape((M, W), order='F').astype(np.uint8)
    I3_new = C[2*Sum:3*Sum].reshape((M, W), order='F').astype(np.uint8)

    return np.stack([I1_new, I2_new, I3_new], axis=2)


def decryption(image, key):
    """
    decrypt the image with key
    
    :param image: encrypted image, format: numpy
    :param key: chaos key
    """
    if not isinstance(image, np.ndarray):
        image = np.array(image)
    
    # 使用 float64 进行计算以确保模运算 (% 256) 的准确性
    M, W, _ = image.shape
    Sum = M * W
    
    p1_val, q1_val = key.split(",")
    p1_val, q1_val = np.float32(p1_val), np.float32(q1_val)
    
    # 获取混沌矩阵 (必须确保与加密时生成的序列完全一致)
    RR, RG, RB, p, q = get_R_matrix(W, M, p1_val, q1_val)
    t = np.gcd(M, W)
    Min_val = min(M, W)

    # --- 1. 构造顺次序列 C (对应加密结尾的顺次截取) ---
    # MATLAB: C = [I1(:)' I2(:)' I3(:)']
    f1 = image[:, :, 0].flatten(order='F').astype(np.float64)
    f2 = image[:, :, 1].flatten(order='F').astype(np.float64)
    f3 = image[:, :, 2].flatten(order='F').astype(np.float64)
    C = np.concatenate([f1, f2, f3])

    total_len = 3 * Sum
    D = np.zeros(total_len)
    E = np.zeros(total_len)
    S1 = np.floor(256 * (p + q) / 2).flatten()
    S2 = np.floor(256 * p).flatten()

    # --- 2. 逆向还原正向扩散 (还原 C -> B) ---
    # 对应加密: C(i) = mod(C(i-1) + B(i) + S2(i), 256)
    D[1:] = (C[1:] - C[:-1] - S2[1:]) % 256
    D[0] = (C[0] - S2[0]) % 256

    # --- 3. 逆向还原逆向扩散 (还原 B -> A) ---
    # 对应加密: B(i) = mod(B(i+1) + S1(i) + A(i), 256)
    E[:-1] = (D[:-1] - D[1:] - S1[:-1]) % 256
    E[-1] = (D[-1] - S1[-1]) % 256

    # --- 4. 按照交替模式提取通道数据 (对应加密开头的 [I1(:) I2(:) I3(:)]') ---
    # E 的结构是 [R1, G1, B1, R2, G2, B2 ...]
    I1 = E[0::3].reshape((M, W), order='F')
    I2 = E[1::3].reshape((M, W), order='F')
    I3 = E[2::3].reshape((M, W), order='F')

    # --- 5. 逆置换 (Scrambling Recovery) ---
    # 置换还原必须是加密步骤的完全倒序：先还原列，再还原行
    # 注意：加密循环是正序，解密必须是逆序 (range 的逆序处理)
    for i in range(((M - t) // t) * t, -1, -t):
        for j in range(((W - t) // t) * t, -1, -t):
            # 确保索引不会越界
            wi = min(int(np.floor(RR[i, j] * M)), M - 1)
            wj = min(int(np.floor(RG[i, j] * W)), W - 1)
            wy = min(int(np.floor(RB[i, j] * Min_val)), Min_val - 1)

            # 还原列变换 (加密是向下移动 wy，解密是向上移动 -wy)
            col_combined = np.concatenate([I1[:, wj], I2[:, wj], I3[:, wj]])
            col_rolled = np.roll(col_combined, -wy) 
            I1[:, wj] = col_rolled[0:M]
            I2[:, wj] = col_rolled[M:2*M]
            I3[:, wj] = col_rolled[2*M:3*M]

            # 还原行变换 (加密是向右移动 wy，解密是向左移动 -wy)
            row_combined = np.concatenate([I1[wi, :], I2[wi, :], I3[wi, :]])
            row_rolled = np.roll(row_combined, -wy)
            I1[wi, :] = row_rolled[0:W]
            I2[wi, :] = row_rolled[W:2*W]
            I3[wi, :] = row_rolled[2*W:3*W]

    # 将 float64 转回 uint8 并堆叠通道
    return np.stack([I1, I2, I3], axis=2).astype(np.uint8)