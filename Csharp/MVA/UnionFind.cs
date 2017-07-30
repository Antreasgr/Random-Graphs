namespace MVA
{
    using System.Collections.Generic;
    using System.Linq;

    public class UnionFind<T>
    {
        public UnionFind()
        {
            this.Weights = new Dictionary<T, int>();
            this.Parents = new Dictionary<T, T>();
        }

        public Dictionary<T, int> Weights { get; private set; }

        public Dictionary<T, T> Parents { get; private set; }

        public T this[T key]
        {
            get
            {
                if (!this.Parents.ContainsKey(key))
                {
                    this.Parents[key] = key;
                    this.Weights[key] = 1;
                    return key;
                }

                var path = new List<T>() { key };
                var root = this.Parents[key];
                while (!root.Equals(path[path.Count - 1]))
                {
                    path.Add(root);
                    root = this.Parents[root];
                }

                foreach (var ancestor in path)
                {
                    this.Parents[ancestor] = root;
                }

                return root;
            }
        }


        public T Union(T a, T b)
        {
            T rootA = this[a], rootB = this[b];
            if (this.Weights[b] > this.Weights[a])
            {
                // make rootA heaviest
                var tmp = rootA;
                rootA = rootB;
                rootB = tmp;
            }

            // rootA is heaviest
            this.Weights[rootA] += this.Weights[rootB];
            this.Parents[rootB] = rootA;

            return rootA;
        }

        public T Union(IEnumerable<T> objects)
        {
            var roots = objects.Select(x => this[x]);
            // var heaviest = roots.Select(r => new { Key = this.Weights[r], Weight = r }).Max(r => r.Weight);
            var heaviest = roots.First();
            foreach (var r in roots.Where(r => !r.Equals(heaviest)))
            {
                this.Weights[heaviest] += this.Weights[r];
                this.Parents[r] = heaviest;
            }

            return heaviest;
        }
    }
}