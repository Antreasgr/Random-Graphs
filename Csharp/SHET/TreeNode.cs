using System;
using System.Collections.Generic;

namespace SHET
{
    public class TreeNode
    {
        public enum NodeState
        {
            Valid,
            NewCC,
            Dummy,
            Empty
        }

        public TreeNode(int uid)
        {
            this.Uid = uid;
        }

        public NodeState State { get; set; } = NodeState.Valid;

        public List<TreeNode> Adjoint { get; set; } = new List<TreeNode>();

        public Dictionary<int, int> Dx { get; set; } = new Dictionary<int, int>();

        public int Uid { get; private set; }

        public List<int> CliqueList { get; set; } = new List<int>();

        public int SeperationIndex { get; set; } = 0;

        public static List<TreeNode> GenerateTree(int n, Random random)
        {
            var tree = new List<TreeNode>() { new TreeNode(0) };
            for (int i = 0; i < n - 1; i++)
            {
                var node = new TreeNode(i + 1);
                var parent = tree[random.Next(tree.Count)];

                parent.Adjoint.Add(node);
                node.Adjoint.Add(parent);

                parent.Dx.Add(node.Uid, parent.Adjoint.Count - 1);
                node.Dx.Add(parent.Uid, node.Adjoint.Count - 1);

                tree.Add(node);
            }

            return tree;
        }

        public static void SubTreeGeneration(List<TreeNode> tree, int k, int treeIndex, Random random)
        {
            
            var n = tree.Count;
            var subTree = new List<TreeNode>();
            var firstNode = tree[random.Next(n)];
            firstNode.CliqueList.Add(treeIndex);
            subTree.Add(firstNode);

            if (k <= 1)
            {
                return;
            }

            var ki = random.Next(1, 2 * k - 1);
            var sy = 0;
            for (int i = 0; i < ki; i++)
            {
                var yi = random.Next(sy, subTree.Count);
                var y = subTree[yi];

                var zi = y.SeperationIndex; // random.Next(y.SeperationIndex, n)
                var z = y.Adjoint[zi];

                subTree.Add(z);
                z.CliqueList.Add(treeIndex);

                if (zi != y.SeperationIndex)
                {
                    var tmp = y.Adjoint[zi];
                    y.Adjoint[zi] = y.Adjoint[y.SeperationIndex];
                    y.Adjoint[y.SeperationIndex] = tmp;
                    y.Dx[z.Uid] = y.SeperationIndex;
                    y.Dx[y.Adjoint[zi].Uid] = zi;
                }

                y.SeperationIndex += 1;

                if (z.Adjoint[z.SeperationIndex] != y)
                {
                    var yzi = z.Dx[y.Uid];
                    var tmp = z.Adjoint[yzi];
                    z.Adjoint[yzi] = z.Adjoint[z.SeperationIndex];
                    z.Adjoint[z.SeperationIndex] = tmp;
                    z.Dx[y.Uid] = z.SeperationIndex;
                    z.Dx[z.Adjoint[yzi].Uid] = yzi;
                }
                z.SeperationIndex += 1;

                if (y.SeperationIndex > y.Adjoint.Count - 1)
                {
                    var tmp = subTree[sy];
                    subTree[sy] = subTree[yi];
                    subTree[yi] = tmp;
                    sy += 1;
                }

                if (z.Adjoint.Count == 1)
                {
                    var tmp = subTree[sy];
                    subTree[sy] = subTree[subTree.Count - 1];
                    subTree[subTree.Count - 1] = tmp;
                    sy += 1;
                }
            }

            foreach (var node in tree)
            {
                node.SeperationIndex = 0;
            }
        }
    }
}