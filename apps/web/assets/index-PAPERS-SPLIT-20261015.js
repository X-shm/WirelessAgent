function Ay(e, t) {
  for (var n = 0; n < t.length; n++) {
    const r = t[n];
    if (typeof r != "string" && !Array.isArray(r)) {
      for (const i in r)
        if (i !== "default" && !(i in e)) {
          const o = Object.getOwnPropertyDescriptor(r, i);
          o &&
            Object.defineProperty(
              e,
              i,
              o.get ? o : { enumerable: !0, get: () => r[i] },
            );
        }
    }
  }
  return Object.freeze(
    Object.defineProperty(e, Symbol.toStringTag, { value: "Module" }),
  );
}
(function () {
  const t = document.createElement("link").relList;
  if (t && t.supports && t.supports("modulepreload")) return;
  for (const i of document.querySelectorAll('link[rel="modulepreload"]')) r(i);
  new MutationObserver((i) => {
    for (const o of i)
      if (o.type === "childList")
        for (const l of o.addedNodes)
          l.tagName === "LINK" && l.rel === "modulepreload" && r(l);
  }).observe(document, { childList: !0, subtree: !0 });
  function n(i) {
    const o = {};
    return (
      i.integrity && (o.integrity = i.integrity),
      i.referrerPolicy && (o.referrerPolicy = i.referrerPolicy),
      i.crossOrigin === "use-credentials"
        ? (o.credentials = "include")
        : i.crossOrigin === "anonymous"
          ? (o.credentials = "omit")
          : (o.credentials = "same-origin"),
      o
    );
  }
  function r(i) {
    if (i.ep) return;
    i.ep = !0;
    const o = n(i);
    fetch(i.href, o);
  }
})();
var Zo =
  typeof globalThis < "u"
    ? globalThis
    : typeof window < "u"
      ? window
      : typeof global < "u"
        ? global
        : typeof self < "u"
          ? self
          : {};
function Rl(e) {
  return e && e.__esModule && Object.prototype.hasOwnProperty.call(e, "default")
    ? e.default
    : e;
}
var dp = { exports: {} },
  Ol = {},
  fp = { exports: {} },
  te = {};
/**
 * @license React
 * react.production.min.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */ var Zi = Symbol.for("react.element"),
  Ry = Symbol.for("react.portal"),
  Oy = Symbol.for("react.fragment"),
  Iy = Symbol.for("react.strict_mode"),
  My = Symbol.for("react.profiler"),
  Ly = Symbol.for("react.provider"),
  Dy = Symbol.for("react.context"),
  Py = Symbol.for("react.forward_ref"),
  zy = Symbol.for("react.suspense"),
  Fy = Symbol.for("react.memo"),
  By = Symbol.for("react.lazy"),
  Tc = Symbol.iterator;
function Uy(e) {
  return e === null || typeof e != "object"
    ? null
    : ((e = (Tc && e[Tc]) || e["@@iterator"]),
      typeof e == "function" ? e : null);
}
var pp = {
    isMounted: function () {
      return !1;
    },
    enqueueForceUpdate: function () {},
    enqueueReplaceState: function () {},
    enqueueSetState: function () {},
  },
  hp = Object.assign,
  gp = {};
function $r(e, t, n) {
  ((this.props = e),
    (this.context = t),
    (this.refs = gp),
    (this.updater = n || pp));
}
$r.prototype.isReactComponent = {};
$r.prototype.setState = function (e, t) {
  if (typeof e != "object" && typeof e != "function" && e != null)
    throw Error(
      "setState(...): takes an object of state variables to update or a function which returns an object of state variables.",
    );
  this.updater.enqueueSetState(this, e, t, "setState");
};
$r.prototype.forceUpdate = function (e) {
  this.updater.enqueueForceUpdate(this, e, "forceUpdate");
};
function mp() {}
mp.prototype = $r.prototype;
function iu(e, t, n) {
  ((this.props = e),
    (this.context = t),
    (this.refs = gp),
    (this.updater = n || pp));
}
var ou = (iu.prototype = new mp());
ou.constructor = iu;
hp(ou, $r.prototype);
ou.isPureReactComponent = !0;
var Ac = Array.isArray,
  yp = Object.prototype.hasOwnProperty,
  lu = { current: null },
  bp = { key: !0, ref: !0, __self: !0, __source: !0 };
function vp(e, t, n) {
  var r,
    i = {},
    o = null,
    l = null;
  if (t != null)
    for (r in (t.ref !== void 0 && (l = t.ref),
    t.key !== void 0 && (o = "" + t.key),
    t))
      yp.call(t, r) && !bp.hasOwnProperty(r) && (i[r] = t[r]);
  var a = arguments.length - 2;
  if (a === 1) i.children = n;
  else if (1 < a) {
    for (var s = Array(a), u = 0; u < a; u++) s[u] = arguments[u + 2];
    i.children = s;
  }
  if (e && e.defaultProps)
    for (r in ((a = e.defaultProps), a)) i[r] === void 0 && (i[r] = a[r]);
  return {
    $$typeof: Zi,
    type: e,
    key: o,
    ref: l,
    props: i,
    _owner: lu.current,
  };
}
function $y(e, t) {
  return {
    $$typeof: Zi,
    type: e.type,
    key: t,
    ref: e.ref,
    props: e.props,
    _owner: e._owner,
  };
}
function au(e) {
  return typeof e == "object" && e !== null && e.$$typeof === Zi;
}
function Hy(e) {
  var t = { "=": "=0", ":": "=2" };
  return (
    "$" +
    e.replace(/[=:]/g, function (n) {
      return t[n];
    })
  );
}
var Rc = /\/+/g;
function ta(e, t) {
  return typeof e == "object" && e !== null && e.key != null
    ? Hy("" + e.key)
    : t.toString(36);
}
function Po(e, t, n, r, i) {
  var o = typeof e;
  (o === "undefined" || o === "boolean") && (e = null);
  var l = !1;
  if (e === null) l = !0;
  else
    switch (o) {
      case "string":
      case "number":
        l = !0;
        break;
      case "object":
        switch (e.$$typeof) {
          case Zi:
          case Ry:
            l = !0;
        }
    }
  if (l)
    return (
      (l = e),
      (i = i(l)),
      (e = r === "" ? "." + ta(l, 0) : r),
      Ac(i)
        ? ((n = ""),
          e != null && (n = e.replace(Rc, "$&/") + "/"),
          Po(i, t, n, "", function (u) {
            return u;
          }))
        : i != null &&
          (au(i) &&
            (i = $y(
              i,
              n +
                (!i.key || (l && l.key === i.key)
                  ? ""
                  : ("" + i.key).replace(Rc, "$&/") + "/") +
                e,
            )),
          t.push(i)),
      1
    );
  if (((l = 0), (r = r === "" ? "." : r + ":"), Ac(e)))
    for (var a = 0; a < e.length; a++) {
      o = e[a];
      var s = r + ta(o, a);
      l += Po(o, t, n, s, i);
    }
  else if (((s = Uy(e)), typeof s == "function"))
    for (e = s.call(e), a = 0; !(o = e.next()).done;)
      ((o = o.value), (s = r + ta(o, a++)), (l += Po(o, t, n, s, i)));
  else if (o === "object")
    throw (
      (t = String(e)),
      Error(
        "Objects are not valid as a React child (found: " +
          (t === "[object Object]"
            ? "object with keys {" + Object.keys(e).join(", ") + "}"
            : t) +
          "). If you meant to render a collection of children, use an array instead.",
      )
    );
  return l;
}
function so(e, t, n) {
  if (e == null) return e;
  var r = [],
    i = 0;
  return (
    Po(e, r, "", "", function (o) {
      return t.call(n, o, i++);
    }),
    r
  );
}
function jy(e) {
  if (e._status === -1) {
    var t = e._result;
    ((t = t()),
      t.then(
        function (n) {
          (e._status === 0 || e._status === -1) &&
            ((e._status = 1), (e._result = n));
        },
        function (n) {
          (e._status === 0 || e._status === -1) &&
            ((e._status = 2), (e._result = n));
        },
      ),
      e._status === -1 && ((e._status = 0), (e._result = t)));
  }
  if (e._status === 1) return e._result.default;
  throw e._result;
}
var Ve = { current: null },
  zo = { transition: null },
  Wy = {
    ReactCurrentDispatcher: Ve,
    ReactCurrentBatchConfig: zo,
    ReactCurrentOwner: lu,
  };
function Ep() {
  throw Error("act(...) is not supported in production builds of React.");
}
te.Children = {
  map: so,
  forEach: function (e, t, n) {
    so(
      e,
      function () {
        t.apply(this, arguments);
      },
      n,
    );
  },
  count: function (e) {
    var t = 0;
    return (
      so(e, function () {
        t++;
      }),
      t
    );
  },
  toArray: function (e) {
    return (
      so(e, function (t) {
        return t;
      }) || []
    );
  },
  only: function (e) {
    if (!au(e))
      throw Error(
        "React.Children.only expected to receive a single React element child.",
      );
    return e;
  },
};
te.Component = $r;
te.Fragment = Oy;
te.Profiler = My;
te.PureComponent = iu;
te.StrictMode = Iy;
te.Suspense = zy;
te.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED = Wy;
te.act = Ep;
te.cloneElement = function (e, t, n) {
  if (e == null)
    throw Error(
      "React.cloneElement(...): The argument must be a React element, but you passed " +
        e +
        ".",
    );
  var r = hp({}, e.props),
    i = e.key,
    o = e.ref,
    l = e._owner;
  if (t != null) {
    if (
      (t.ref !== void 0 && ((o = t.ref), (l = lu.current)),
      t.key !== void 0 && (i = "" + t.key),
      e.type && e.type.defaultProps)
    )
      var a = e.type.defaultProps;
    for (s in t)
      yp.call(t, s) &&
        !bp.hasOwnProperty(s) &&
        (r[s] = t[s] === void 0 && a !== void 0 ? a[s] : t[s]);
  }
  var s = arguments.length - 2;
  if (s === 1) r.children = n;
  else if (1 < s) {
    a = Array(s);
    for (var u = 0; u < s; u++) a[u] = arguments[u + 2];
    r.children = a;
  }
  return { $$typeof: Zi, type: e.type, key: i, ref: o, props: r, _owner: l };
};
te.createContext = function (e) {
  return (
    (e = {
      $$typeof: Dy,
      _currentValue: e,
      _currentValue2: e,
      _threadCount: 0,
      Provider: null,
      Consumer: null,
      _defaultValue: null,
      _globalName: null,
    }),
    (e.Provider = { $$typeof: Ly, _context: e }),
    (e.Consumer = e)
  );
};
te.createElement = vp;
te.createFactory = function (e) {
  var t = vp.bind(null, e);
  return ((t.type = e), t);
};
te.createRef = function () {
  return { current: null };
};
te.forwardRef = function (e) {
  return { $$typeof: Py, render: e };
};
te.isValidElement = au;
te.lazy = function (e) {
  return { $$typeof: By, _payload: { _status: -1, _result: e }, _init: jy };
};
te.memo = function (e, t) {
  return { $$typeof: Fy, type: e, compare: t === void 0 ? null : t };
};
te.startTransition = function (e) {
  var t = zo.transition;
  zo.transition = {};
  try {
    e();
  } finally {
    zo.transition = t;
  }
};
te.unstable_act = Ep;
te.useCallback = function (e, t) {
  return Ve.current.useCallback(e, t);
};
te.useContext = function (e) {
  return Ve.current.useContext(e);
};
te.useDebugValue = function () {};
te.useDeferredValue = function (e) {
  return Ve.current.useDeferredValue(e);
};
te.useEffect = function (e, t) {
  return Ve.current.useEffect(e, t);
};
te.useId = function () {
  return Ve.current.useId();
};
te.useImperativeHandle = function (e, t, n) {
  return Ve.current.useImperativeHandle(e, t, n);
};
te.useInsertionEffect = function (e, t) {
  return Ve.current.useInsertionEffect(e, t);
};
te.useLayoutEffect = function (e, t) {
  return Ve.current.useLayoutEffect(e, t);
};
te.useMemo = function (e, t) {
  return Ve.current.useMemo(e, t);
};
te.useReducer = function (e, t, n) {
  return Ve.current.useReducer(e, t, n);
};
te.useRef = function (e) {
  return Ve.current.useRef(e);
};
te.useState = function (e) {
  return Ve.current.useState(e);
};
te.useSyncExternalStore = function (e, t, n) {
  return Ve.current.useSyncExternalStore(e, t, n);
};
te.useTransition = function () {
  return Ve.current.useTransition();
};
te.version = "18.3.1";
fp.exports = te;
var D = fp.exports;
const wp = Rl(D),
  Gy = Ay({ __proto__: null, default: wp }, [D]);
/**
 * @license React
 * react-jsx-runtime.production.min.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */ var Ky = D,
  Vy = Symbol.for("react.element"),
  qy = Symbol.for("react.fragment"),
  Yy = Object.prototype.hasOwnProperty,
  Qy = Ky.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED.ReactCurrentOwner,
  Zy = { key: !0, ref: !0, __self: !0, __source: !0 };
function xp(e, t, n) {
  var r,
    i = {},
    o = null,
    l = null;
  (n !== void 0 && (o = "" + n),
    t.key !== void 0 && (o = "" + t.key),
    t.ref !== void 0 && (l = t.ref));
  for (r in t) Yy.call(t, r) && !Zy.hasOwnProperty(r) && (i[r] = t[r]);
  if (e && e.defaultProps)
    for (r in ((t = e.defaultProps), t)) i[r] === void 0 && (i[r] = t[r]);
  return {
    $$typeof: Vy,
    type: e,
    key: o,
    ref: l,
    props: i,
    _owner: Qy.current,
  };
}
Ol.Fragment = qy;
Ol.jsx = xp;
Ol.jsxs = xp;
dp.exports = Ol;
var T = dp.exports,
  Va = {},
  _p = { exports: {} },
  ct = {},
  kp = { exports: {} },
  Sp = {};
/**
 * @license React
 * scheduler.production.min.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */ (function (e) {
  function t(C, M) {
    var v = C.length;
    C.push(M);
    e: for (; 0 < v;) {
      var H = (v - 1) >>> 1,
        K = C[H];
      if (0 < i(K, M)) ((C[H] = M), (C[v] = K), (v = H));
      else break e;
    }
  }
  function n(C) {
    return C.length === 0 ? null : C[0];
  }
  function r(C) {
    if (C.length === 0) return null;
    var M = C[0],
      v = C.pop();
    if (v !== M) {
      C[0] = v;
      e: for (var H = 0, K = C.length, w = K >>> 1; H < w;) {
        var ne = 2 * (H + 1) - 1,
          pe = C[ne],
          oe = ne + 1,
          $e = C[oe];
        if (0 > i(pe, v))
          oe < K && 0 > i($e, pe)
            ? ((C[H] = $e), (C[oe] = v), (H = oe))
            : ((C[H] = pe), (C[ne] = v), (H = ne));
        else if (oe < K && 0 > i($e, v)) ((C[H] = $e), (C[oe] = v), (H = oe));
        else break e;
      }
    }
    return M;
  }
  function i(C, M) {
    var v = C.sortIndex - M.sortIndex;
    return v !== 0 ? v : C.id - M.id;
  }
  if (typeof performance == "object" && typeof performance.now == "function") {
    var o = performance;
    e.unstable_now = function () {
      return o.now();
    };
  } else {
    var l = Date,
      a = l.now();
    e.unstable_now = function () {
      return l.now() - a;
    };
  }
  var s = [],
    u = [],
    d = 1,
    c = null,
    f = 3,
    p = !1,
    g = !1,
    y = !1,
    E = typeof setTimeout == "function" ? setTimeout : null,
    h = typeof clearTimeout == "function" ? clearTimeout : null,
    m = typeof setImmediate < "u" ? setImmediate : null;
  typeof navigator < "u" &&
    navigator.scheduling !== void 0 &&
    navigator.scheduling.isInputPending !== void 0 &&
    navigator.scheduling.isInputPending.bind(navigator.scheduling);
  function b(C) {
    for (var M = n(u); M !== null;) {
      if (M.callback === null) r(u);
      else if (M.startTime <= C)
        (r(u), (M.sortIndex = M.expirationTime), t(s, M));
      else break;
      M = n(u);
    }
  }
  function _(C) {
    if (((y = !1), b(C), !g))
      if (n(s) !== null) ((g = !0), R(N));
      else {
        var M = n(u);
        M !== null && B(_, M.startTime - C);
      }
  }
  function N(C, M) {
    ((g = !1), y && ((y = !1), h(I), (I = -1)), (p = !0));
    var v = f;
    try {
      for (
        b(M), c = n(s);
        c !== null && (!(c.expirationTime > M) || (C && !F()));
      ) {
        var H = c.callback;
        if (typeof H == "function") {
          ((c.callback = null), (f = c.priorityLevel));
          var K = H(c.expirationTime <= M);
          ((M = e.unstable_now()),
            typeof K == "function" ? (c.callback = K) : c === n(s) && r(s),
            b(M));
        } else r(s);
        c = n(s);
      }
      if (c !== null) var w = !0;
      else {
        var ne = n(u);
        (ne !== null && B(_, ne.startTime - M), (w = !1));
      }
      return w;
    } finally {
      ((c = null), (f = v), (p = !1));
    }
  }
  var x = !1,
    O = null,
    I = -1,
    U = 5,
    S = -1;
  function F() {
    return !(e.unstable_now() - S < U);
  }
  function L() {
    if (O !== null) {
      var C = e.unstable_now();
      S = C;
      var M = !0;
      try {
        M = O(!0, C);
      } finally {
        M ? Q() : ((x = !1), (O = null));
      }
    } else x = !1;
  }
  var Q;
  if (typeof m == "function")
    Q = function () {
      m(L);
    };
  else if (typeof MessageChannel < "u") {
    var V = new MessageChannel(),
      G = V.port2;
    ((V.port1.onmessage = L),
      (Q = function () {
        G.postMessage(null);
      }));
  } else
    Q = function () {
      E(L, 0);
    };
  function R(C) {
    ((O = C), x || ((x = !0), Q()));
  }
  function B(C, M) {
    I = E(function () {
      C(e.unstable_now());
    }, M);
  }
  ((e.unstable_IdlePriority = 5),
    (e.unstable_ImmediatePriority = 1),
    (e.unstable_LowPriority = 4),
    (e.unstable_NormalPriority = 3),
    (e.unstable_Profiling = null),
    (e.unstable_UserBlockingPriority = 2),
    (e.unstable_cancelCallback = function (C) {
      C.callback = null;
    }),
    (e.unstable_continueExecution = function () {
      g || p || ((g = !0), R(N));
    }),
    (e.unstable_forceFrameRate = function (C) {
      0 > C || 125 < C
        ? console.error(
            "forceFrameRate takes a positive int between 0 and 125, forcing frame rates higher than 125 fps is not supported",
          )
        : (U = 0 < C ? Math.floor(1e3 / C) : 5);
    }),
    (e.unstable_getCurrentPriorityLevel = function () {
      return f;
    }),
    (e.unstable_getFirstCallbackNode = function () {
      return n(s);
    }),
    (e.unstable_next = function (C) {
      switch (f) {
        case 1:
        case 2:
        case 3:
          var M = 3;
          break;
        default:
          M = f;
      }
      var v = f;
      f = M;
      try {
        return C();
      } finally {
        f = v;
      }
    }),
    (e.unstable_pauseExecution = function () {}),
    (e.unstable_requestPaint = function () {}),
    (e.unstable_runWithPriority = function (C, M) {
      switch (C) {
        case 1:
        case 2:
        case 3:
        case 4:
        case 5:
          break;
        default:
          C = 3;
      }
      var v = f;
      f = C;
      try {
        return M();
      } finally {
        f = v;
      }
    }),
    (e.unstable_scheduleCallback = function (C, M, v) {
      var H = e.unstable_now();
      switch (
        (typeof v == "object" && v !== null
          ? ((v = v.delay), (v = typeof v == "number" && 0 < v ? H + v : H))
          : (v = H),
        C)
      ) {
        case 1:
          var K = -1;
          break;
        case 2:
          K = 250;
          break;
        case 5:
          K = 1073741823;
          break;
        case 4:
          K = 1e4;
          break;
        default:
          K = 5e3;
      }
      return (
        (K = v + K),
        (C = {
          id: d++,
          callback: M,
          priorityLevel: C,
          startTime: v,
          expirationTime: K,
          sortIndex: -1,
        }),
        v > H
          ? ((C.sortIndex = v),
            t(u, C),
            n(s) === null &&
              C === n(u) &&
              (y ? (h(I), (I = -1)) : (y = !0), B(_, v - H)))
          : ((C.sortIndex = K), t(s, C), g || p || ((g = !0), R(N))),
        C
      );
    }),
    (e.unstable_shouldYield = F),
    (e.unstable_wrapCallback = function (C) {
      var M = f;
      return function () {
        var v = f;
        f = M;
        try {
          return C.apply(this, arguments);
        } finally {
          f = v;
        }
      };
    }));
})(Sp);
kp.exports = Sp;
var Xy = kp.exports;
/**
 * @license React
 * react-dom.production.min.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */ var Jy = D,
  ut = Xy;
function P(e) {
  for (
    var t = "https://reactjs.org/docs/error-decoder.html?invariant=" + e, n = 1;
    n < arguments.length;
    n++
  )
    t += "&args[]=" + encodeURIComponent(arguments[n]);
  return (
    "Minified React error #" +
    e +
    "; visit " +
    t +
    " for the full message or use the non-minified dev environment for full errors and additional helpful warnings."
  );
}
var Np = new Set(),
  Ti = {};
function Xn(e, t) {
  (Ir(e, t), Ir(e + "Capture", t));
}
function Ir(e, t) {
  for (Ti[e] = t, e = 0; e < t.length; e++) Np.add(t[e]);
}
var Qt = !(
    typeof window > "u" ||
    typeof window.document > "u" ||
    typeof window.document.createElement > "u"
  ),
  qa = Object.prototype.hasOwnProperty,
  eb =
    /^[:A-Z_a-z\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u02FF\u0370-\u037D\u037F-\u1FFF\u200C-\u200D\u2070-\u218F\u2C00-\u2FEF\u3001-\uD7FF\uF900-\uFDCF\uFDF0-\uFFFD][:A-Z_a-z\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u02FF\u0370-\u037D\u037F-\u1FFF\u200C-\u200D\u2070-\u218F\u2C00-\u2FEF\u3001-\uD7FF\uF900-\uFDCF\uFDF0-\uFFFD\-.0-9\u00B7\u0300-\u036F\u203F-\u2040]*$/,
  Oc = {},
  Ic = {};
function tb(e) {
  return qa.call(Ic, e)
    ? !0
    : qa.call(Oc, e)
      ? !1
      : eb.test(e)
        ? (Ic[e] = !0)
        : ((Oc[e] = !0), !1);
}
function nb(e, t, n, r) {
  if (n !== null && n.type === 0) return !1;
  switch (typeof t) {
    case "function":
    case "symbol":
      return !0;
    case "boolean":
      return r
        ? !1
        : n !== null
          ? !n.acceptsBooleans
          : ((e = e.toLowerCase().slice(0, 5)), e !== "data-" && e !== "aria-");
    default:
      return !1;
  }
}
function rb(e, t, n, r) {
  if (t === null || typeof t > "u" || nb(e, t, n, r)) return !0;
  if (r) return !1;
  if (n !== null)
    switch (n.type) {
      case 3:
        return !t;
      case 4:
        return t === !1;
      case 5:
        return isNaN(t);
      case 6:
        return isNaN(t) || 1 > t;
    }
  return !1;
}
function qe(e, t, n, r, i, o, l) {
  ((this.acceptsBooleans = t === 2 || t === 3 || t === 4),
    (this.attributeName = r),
    (this.attributeNamespace = i),
    (this.mustUseProperty = n),
    (this.propertyName = e),
    (this.type = t),
    (this.sanitizeURL = o),
    (this.removeEmptyString = l));
}
var Le = {};
"children dangerouslySetInnerHTML defaultValue defaultChecked innerHTML suppressContentEditableWarning suppressHydrationWarning style"
  .split(" ")
  .forEach(function (e) {
    Le[e] = new qe(e, 0, !1, e, null, !1, !1);
  });
[
  ["acceptCharset", "accept-charset"],
  ["className", "class"],
  ["htmlFor", "for"],
  ["httpEquiv", "http-equiv"],
].forEach(function (e) {
  var t = e[0];
  Le[t] = new qe(t, 1, !1, e[1], null, !1, !1);
});
["contentEditable", "draggable", "spellCheck", "value"].forEach(function (e) {
  Le[e] = new qe(e, 2, !1, e.toLowerCase(), null, !1, !1);
});
[
  "autoReverse",
  "externalResourcesRequired",
  "focusable",
  "preserveAlpha",
].forEach(function (e) {
  Le[e] = new qe(e, 2, !1, e, null, !1, !1);
});
"allowFullScreen async autoFocus autoPlay controls default defer disabled disablePictureInPicture disableRemotePlayback formNoValidate hidden loop noModule noValidate open playsInline readOnly required reversed scoped seamless itemScope"
  .split(" ")
  .forEach(function (e) {
    Le[e] = new qe(e, 3, !1, e.toLowerCase(), null, !1, !1);
  });
["checked", "multiple", "muted", "selected"].forEach(function (e) {
  Le[e] = new qe(e, 3, !0, e, null, !1, !1);
});
["capture", "download"].forEach(function (e) {
  Le[e] = new qe(e, 4, !1, e, null, !1, !1);
});
["cols", "rows", "size", "span"].forEach(function (e) {
  Le[e] = new qe(e, 6, !1, e, null, !1, !1);
});
["rowSpan", "start"].forEach(function (e) {
  Le[e] = new qe(e, 5, !1, e.toLowerCase(), null, !1, !1);
});
var su = /[\-:]([a-z])/g;
function uu(e) {
  return e[1].toUpperCase();
}
"accent-height alignment-baseline arabic-form baseline-shift cap-height clip-path clip-rule color-interpolation color-interpolation-filters color-profile color-rendering dominant-baseline enable-background fill-opacity fill-rule flood-color flood-opacity font-family font-size font-size-adjust font-stretch font-style font-variant font-weight glyph-name glyph-orientation-horizontal glyph-orientation-vertical horiz-adv-x horiz-origin-x image-rendering letter-spacing lighting-color marker-end marker-mid marker-start overline-position overline-thickness paint-order panose-1 pointer-events rendering-intent shape-rendering stop-color stop-opacity strikethrough-position strikethrough-thickness stroke-dasharray stroke-dashoffset stroke-linecap stroke-linejoin stroke-miterlimit stroke-opacity stroke-width text-anchor text-decoration text-rendering underline-position underline-thickness unicode-bidi unicode-range units-per-em v-alphabetic v-hanging v-ideographic v-mathematical vector-effect vert-adv-y vert-origin-x vert-origin-y word-spacing writing-mode xmlns:xlink x-height"
  .split(" ")
  .forEach(function (e) {
    var t = e.replace(su, uu);
    Le[t] = new qe(t, 1, !1, e, null, !1, !1);
  });
"xlink:actuate xlink:arcrole xlink:role xlink:show xlink:title xlink:type"
  .split(" ")
  .forEach(function (e) {
    var t = e.replace(su, uu);
    Le[t] = new qe(t, 1, !1, e, "http://www.w3.org/1999/xlink", !1, !1);
  });
["xml:base", "xml:lang", "xml:space"].forEach(function (e) {
  var t = e.replace(su, uu);
  Le[t] = new qe(t, 1, !1, e, "http://www.w3.org/XML/1998/namespace", !1, !1);
});
["tabIndex", "crossOrigin"].forEach(function (e) {
  Le[e] = new qe(e, 1, !1, e.toLowerCase(), null, !1, !1);
});
Le.xlinkHref = new qe(
  "xlinkHref",
  1,
  !1,
  "xlink:href",
  "http://www.w3.org/1999/xlink",
  !0,
  !1,
);
["src", "href", "action", "formAction"].forEach(function (e) {
  Le[e] = new qe(e, 1, !1, e.toLowerCase(), null, !0, !0);
});
function cu(e, t, n, r) {
  var i = Le.hasOwnProperty(t) ? Le[t] : null;
  (i !== null
    ? i.type !== 0
    : r ||
      !(2 < t.length) ||
      (t[0] !== "o" && t[0] !== "O") ||
      (t[1] !== "n" && t[1] !== "N")) &&
    (rb(t, n, i, r) && (n = null),
    r || i === null
      ? tb(t) && (n === null ? e.removeAttribute(t) : e.setAttribute(t, "" + n))
      : i.mustUseProperty
        ? (e[i.propertyName] = n === null ? (i.type === 3 ? !1 : "") : n)
        : ((t = i.attributeName),
          (r = i.attributeNamespace),
          n === null
            ? e.removeAttribute(t)
            : ((i = i.type),
              (n = i === 3 || (i === 4 && n === !0) ? "" : "" + n),
              r ? e.setAttributeNS(r, t, n) : e.setAttribute(t, n))));
}
var en = Jy.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED,
  uo = Symbol.for("react.element"),
  fr = Symbol.for("react.portal"),
  pr = Symbol.for("react.fragment"),
  du = Symbol.for("react.strict_mode"),
  Ya = Symbol.for("react.profiler"),
  Cp = Symbol.for("react.provider"),
  Tp = Symbol.for("react.context"),
  fu = Symbol.for("react.forward_ref"),
  Qa = Symbol.for("react.suspense"),
  Za = Symbol.for("react.suspense_list"),
  pu = Symbol.for("react.memo"),
  cn = Symbol.for("react.lazy"),
  Ap = Symbol.for("react.offscreen"),
  Mc = Symbol.iterator;
function Jr(e) {
  return e === null || typeof e != "object"
    ? null
    : ((e = (Mc && e[Mc]) || e["@@iterator"]),
      typeof e == "function" ? e : null);
}
var Ee = Object.assign,
  na;
function fi(e) {
  if (na === void 0)
    try {
      throw Error();
    } catch (n) {
      var t = n.stack.trim().match(/\n( *(at )?)/);
      na = (t && t[1]) || "";
    }
  return (
    `
` +
    na +
    e
  );
}
var ra = !1;
function ia(e, t) {
  if (!e || ra) return "";
  ra = !0;
  var n = Error.prepareStackTrace;
  Error.prepareStackTrace = void 0;
  try {
    if (t)
      if (
        ((t = function () {
          throw Error();
        }),
        Object.defineProperty(t.prototype, "props", {
          set: function () {
            throw Error();
          },
        }),
        typeof Reflect == "object" && Reflect.construct)
      ) {
        try {
          Reflect.construct(t, []);
        } catch (u) {
          var r = u;
        }
        Reflect.construct(e, [], t);
      } else {
        try {
          t.call();
        } catch (u) {
          r = u;
        }
        e.call(t.prototype);
      }
    else {
      try {
        throw Error();
      } catch (u) {
        r = u;
      }
      e();
    }
  } catch (u) {
    if (u && r && typeof u.stack == "string") {
      for (
        var i = u.stack.split(`
`),
          o = r.stack.split(`
`),
          l = i.length - 1,
          a = o.length - 1;
        1 <= l && 0 <= a && i[l] !== o[a];
      )
        a--;
      for (; 1 <= l && 0 <= a; l--, a--)
        if (i[l] !== o[a]) {
          if (l !== 1 || a !== 1)
            do
              if ((l--, a--, 0 > a || i[l] !== o[a])) {
                var s =
                  `
` + i[l].replace(" at new ", " at ");
                return (
                  e.displayName &&
                    s.includes("<anonymous>") &&
                    (s = s.replace("<anonymous>", e.displayName)),
                  s
                );
              }
            while (1 <= l && 0 <= a);
          break;
        }
    }
  } finally {
    ((ra = !1), (Error.prepareStackTrace = n));
  }
  return (e = e ? e.displayName || e.name : "") ? fi(e) : "";
}
function ib(e) {
  switch (e.tag) {
    case 5:
      return fi(e.type);
    case 16:
      return fi("Lazy");
    case 13:
      return fi("Suspense");
    case 19:
      return fi("SuspenseList");
    case 0:
    case 2:
    case 15:
      return ((e = ia(e.type, !1)), e);
    case 11:
      return ((e = ia(e.type.render, !1)), e);
    case 1:
      return ((e = ia(e.type, !0)), e);
    default:
      return "";
  }
}
function Xa(e) {
  if (e == null) return null;
  if (typeof e == "function") return e.displayName || e.name || null;
  if (typeof e == "string") return e;
  switch (e) {
    case pr:
      return "Fragment";
    case fr:
      return "Portal";
    case Ya:
      return "Profiler";
    case du:
      return "StrictMode";
    case Qa:
      return "Suspense";
    case Za:
      return "SuspenseList";
  }
  if (typeof e == "object")
    switch (e.$$typeof) {
      case Tp:
        return (e.displayName || "Context") + ".Consumer";
      case Cp:
        return (e._context.displayName || "Context") + ".Provider";
      case fu:
        var t = e.render;
        return (
          (e = e.displayName),
          e ||
            ((e = t.displayName || t.name || ""),
            (e = e !== "" ? "ForwardRef(" + e + ")" : "ForwardRef")),
          e
        );
      case pu:
        return (
          (t = e.displayName || null),
          t !== null ? t : Xa(e.type) || "Memo"
        );
      case cn:
        ((t = e._payload), (e = e._init));
        try {
          return Xa(e(t));
        } catch {}
    }
  return null;
}
function ob(e) {
  var t = e.type;
  switch (e.tag) {
    case 24:
      return "Cache";
    case 9:
      return (t.displayName || "Context") + ".Consumer";
    case 10:
      return (t._context.displayName || "Context") + ".Provider";
    case 18:
      return "DehydratedFragment";
    case 11:
      return (
        (e = t.render),
        (e = e.displayName || e.name || ""),
        t.displayName || (e !== "" ? "ForwardRef(" + e + ")" : "ForwardRef")
      );
    case 7:
      return "Fragment";
    case 5:
      return t;
    case 4:
      return "Portal";
    case 3:
      return "Root";
    case 6:
      return "Text";
    case 16:
      return Xa(t);
    case 8:
      return t === du ? "StrictMode" : "Mode";
    case 22:
      return "Offscreen";
    case 12:
      return "Profiler";
    case 21:
      return "Scope";
    case 13:
      return "Suspense";
    case 19:
      return "SuspenseList";
    case 25:
      return "TracingMarker";
    case 1:
    case 0:
    case 17:
    case 2:
    case 14:
    case 15:
      if (typeof t == "function") return t.displayName || t.name || null;
      if (typeof t == "string") return t;
  }
  return null;
}
function Nn(e) {
  switch (typeof e) {
    case "boolean":
    case "number":
    case "string":
    case "undefined":
      return e;
    case "object":
      return e;
    default:
      return "";
  }
}
function Rp(e) {
  var t = e.type;
  return (
    (e = e.nodeName) &&
    e.toLowerCase() === "input" &&
    (t === "checkbox" || t === "radio")
  );
}
function lb(e) {
  var t = Rp(e) ? "checked" : "value",
    n = Object.getOwnPropertyDescriptor(e.constructor.prototype, t),
    r = "" + e[t];
  if (
    !e.hasOwnProperty(t) &&
    typeof n < "u" &&
    typeof n.get == "function" &&
    typeof n.set == "function"
  ) {
    var i = n.get,
      o = n.set;
    return (
      Object.defineProperty(e, t, {
        configurable: !0,
        get: function () {
          return i.call(this);
        },
        set: function (l) {
          ((r = "" + l), o.call(this, l));
        },
      }),
      Object.defineProperty(e, t, { enumerable: n.enumerable }),
      {
        getValue: function () {
          return r;
        },
        setValue: function (l) {
          r = "" + l;
        },
        stopTracking: function () {
          ((e._valueTracker = null), delete e[t]);
        },
      }
    );
  }
}
function co(e) {
  e._valueTracker || (e._valueTracker = lb(e));
}
function Op(e) {
  if (!e) return !1;
  var t = e._valueTracker;
  if (!t) return !0;
  var n = t.getValue(),
    r = "";
  return (
    e && (r = Rp(e) ? (e.checked ? "true" : "false") : e.value),
    (e = r),
    e !== n ? (t.setValue(e), !0) : !1
  );
}
function Xo(e) {
  if (((e = e || (typeof document < "u" ? document : void 0)), typeof e > "u"))
    return null;
  try {
    return e.activeElement || e.body;
  } catch {
    return e.body;
  }
}
function Ja(e, t) {
  var n = t.checked;
  return Ee({}, t, {
    defaultChecked: void 0,
    defaultValue: void 0,
    value: void 0,
    checked: n ?? e._wrapperState.initialChecked,
  });
}
function Lc(e, t) {
  var n = t.defaultValue == null ? "" : t.defaultValue,
    r = t.checked != null ? t.checked : t.defaultChecked;
  ((n = Nn(t.value != null ? t.value : n)),
    (e._wrapperState = {
      initialChecked: r,
      initialValue: n,
      controlled:
        t.type === "checkbox" || t.type === "radio"
          ? t.checked != null
          : t.value != null,
    }));
}
function Ip(e, t) {
  ((t = t.checked), t != null && cu(e, "checked", t, !1));
}
function es(e, t) {
  Ip(e, t);
  var n = Nn(t.value),
    r = t.type;
  if (n != null)
    r === "number"
      ? ((n === 0 && e.value === "") || e.value != n) && (e.value = "" + n)
      : e.value !== "" + n && (e.value = "" + n);
  else if (r === "submit" || r === "reset") {
    e.removeAttribute("value");
    return;
  }
  (t.hasOwnProperty("value")
    ? ts(e, t.type, n)
    : t.hasOwnProperty("defaultValue") && ts(e, t.type, Nn(t.defaultValue)),
    t.checked == null &&
      t.defaultChecked != null &&
      (e.defaultChecked = !!t.defaultChecked));
}
function Dc(e, t, n) {
  if (t.hasOwnProperty("value") || t.hasOwnProperty("defaultValue")) {
    var r = t.type;
    if (!(
      (r !== "submit" && r !== "reset") ||
      (t.value !== void 0 && t.value !== null)
    ))
      return;
    ((t = "" + e._wrapperState.initialValue),
      n || t === e.value || (e.value = t),
      (e.defaultValue = t));
  }
  ((n = e.name),
    n !== "" && (e.name = ""),
    (e.defaultChecked = !!e._wrapperState.initialChecked),
    n !== "" && (e.name = n));
}
function ts(e, t, n) {
  (t !== "number" || Xo(e.ownerDocument) !== e) &&
    (n == null
      ? (e.defaultValue = "" + e._wrapperState.initialValue)
      : e.defaultValue !== "" + n && (e.defaultValue = "" + n));
}
var pi = Array.isArray;
function kr(e, t, n, r) {
  if (((e = e.options), t)) {
    t = {};
    for (var i = 0; i < n.length; i++) t["$" + n[i]] = !0;
    for (n = 0; n < e.length; n++)
      ((i = t.hasOwnProperty("$" + e[n].value)),
        e[n].selected !== i && (e[n].selected = i),
        i && r && (e[n].defaultSelected = !0));
  } else {
    for (n = "" + Nn(n), t = null, i = 0; i < e.length; i++) {
      if (e[i].value === n) {
        ((e[i].selected = !0), r && (e[i].defaultSelected = !0));
        return;
      }
      t !== null || e[i].disabled || (t = e[i]);
    }
    t !== null && (t.selected = !0);
  }
}
function ns(e, t) {
  if (t.dangerouslySetInnerHTML != null) throw Error(P(91));
  return Ee({}, t, {
    value: void 0,
    defaultValue: void 0,
    children: "" + e._wrapperState.initialValue,
  });
}
function Pc(e, t) {
  var n = t.value;
  if (n == null) {
    if (((n = t.children), (t = t.defaultValue), n != null)) {
      if (t != null) throw Error(P(92));
      if (pi(n)) {
        if (1 < n.length) throw Error(P(93));
        n = n[0];
      }
      t = n;
    }
    (t == null && (t = ""), (n = t));
  }
  e._wrapperState = { initialValue: Nn(n) };
}
function Mp(e, t) {
  var n = Nn(t.value),
    r = Nn(t.defaultValue);
  (n != null &&
    ((n = "" + n),
    n !== e.value && (e.value = n),
    t.defaultValue == null && e.defaultValue !== n && (e.defaultValue = n)),
    r != null && (e.defaultValue = "" + r));
}
function zc(e) {
  var t = e.textContent;
  t === e._wrapperState.initialValue && t !== "" && t !== null && (e.value = t);
}
function Lp(e) {
  switch (e) {
    case "svg":
      return "http://www.w3.org/2000/svg";
    case "math":
      return "http://www.w3.org/1998/Math/MathML";
    default:
      return "http://www.w3.org/1999/xhtml";
  }
}
function rs(e, t) {
  return e == null || e === "http://www.w3.org/1999/xhtml"
    ? Lp(t)
    : e === "http://www.w3.org/2000/svg" && t === "foreignObject"
      ? "http://www.w3.org/1999/xhtml"
      : e;
}
var fo,
  Dp = (function (e) {
    return typeof MSApp < "u" && MSApp.execUnsafeLocalFunction
      ? function (t, n, r, i) {
          MSApp.execUnsafeLocalFunction(function () {
            return e(t, n, r, i);
          });
        }
      : e;
  })(function (e, t) {
    if (e.namespaceURI !== "http://www.w3.org/2000/svg" || "innerHTML" in e)
      e.innerHTML = t;
    else {
      for (
        fo = fo || document.createElement("div"),
          fo.innerHTML = "<svg>" + t.valueOf().toString() + "</svg>",
          t = fo.firstChild;
        e.firstChild;
      )
        e.removeChild(e.firstChild);
      for (; t.firstChild;) e.appendChild(t.firstChild);
    }
  });
function Ai(e, t) {
  if (t) {
    var n = e.firstChild;
    if (n && n === e.lastChild && n.nodeType === 3) {
      n.nodeValue = t;
      return;
    }
  }
  e.textContent = t;
}
var mi = {
    animationIterationCount: !0,
    aspectRatio: !0,
    borderImageOutset: !0,
    borderImageSlice: !0,
    borderImageWidth: !0,
    boxFlex: !0,
    boxFlexGroup: !0,
    boxOrdinalGroup: !0,
    columnCount: !0,
    columns: !0,
    flex: !0,
    flexGrow: !0,
    flexPositive: !0,
    flexShrink: !0,
    flexNegative: !0,
    flexOrder: !0,
    gridArea: !0,
    gridRow: !0,
    gridRowEnd: !0,
    gridRowSpan: !0,
    gridRowStart: !0,
    gridColumn: !0,
    gridColumnEnd: !0,
    gridColumnSpan: !0,
    gridColumnStart: !0,
    fontWeight: !0,
    lineClamp: !0,
    lineHeight: !0,
    opacity: !0,
    order: !0,
    orphans: !0,
    tabSize: !0,
    widows: !0,
    zIndex: !0,
    zoom: !0,
    fillOpacity: !0,
    floodOpacity: !0,
    stopOpacity: !0,
    strokeDasharray: !0,
    strokeDashoffset: !0,
    strokeMiterlimit: !0,
    strokeOpacity: !0,
    strokeWidth: !0,
  },
  ab = ["Webkit", "ms", "Moz", "O"];
Object.keys(mi).forEach(function (e) {
  ab.forEach(function (t) {
    ((t = t + e.charAt(0).toUpperCase() + e.substring(1)), (mi[t] = mi[e]));
  });
});
function Pp(e, t, n) {
  return t == null || typeof t == "boolean" || t === ""
    ? ""
    : n || typeof t != "number" || t === 0 || (mi.hasOwnProperty(e) && mi[e])
      ? ("" + t).trim()
      : t + "px";
}
function zp(e, t) {
  e = e.style;
  for (var n in t)
    if (t.hasOwnProperty(n)) {
      var r = n.indexOf("--") === 0,
        i = Pp(n, t[n], r);
      (n === "float" && (n = "cssFloat"), r ? e.setProperty(n, i) : (e[n] = i));
    }
}
var sb = Ee(
  { menuitem: !0 },
  {
    area: !0,
    base: !0,
    br: !0,
    col: !0,
    embed: !0,
    hr: !0,
    img: !0,
    input: !0,
    keygen: !0,
    link: !0,
    meta: !0,
    param: !0,
    source: !0,
    track: !0,
    wbr: !0,
  },
);
function is(e, t) {
  if (t) {
    if (sb[e] && (t.children != null || t.dangerouslySetInnerHTML != null))
      throw Error(P(137, e));
    if (t.dangerouslySetInnerHTML != null) {
      if (t.children != null) throw Error(P(60));
      if (
        typeof t.dangerouslySetInnerHTML != "object" ||
        !("__html" in t.dangerouslySetInnerHTML)
      )
        throw Error(P(61));
    }
    if (t.style != null && typeof t.style != "object") throw Error(P(62));
  }
}
function os(e, t) {
  if (e.indexOf("-") === -1) return typeof t.is == "string";
  switch (e) {
    case "annotation-xml":
    case "color-profile":
    case "font-face":
    case "font-face-src":
    case "font-face-uri":
    case "font-face-format":
    case "font-face-name":
    case "missing-glyph":
      return !1;
    default:
      return !0;
  }
}
var ls = null;
function hu(e) {
  return (
    (e = e.target || e.srcElement || window),
    e.correspondingUseElement && (e = e.correspondingUseElement),
    e.nodeType === 3 ? e.parentNode : e
  );
}
var as = null,
  Sr = null,
  Nr = null;
function Fc(e) {
  if ((e = eo(e))) {
    if (typeof as != "function") throw Error(P(280));
    var t = e.stateNode;
    t && ((t = Pl(t)), as(e.stateNode, e.type, t));
  }
}
function Fp(e) {
  Sr ? (Nr ? Nr.push(e) : (Nr = [e])) : (Sr = e);
}
function Bp() {
  if (Sr) {
    var e = Sr,
      t = Nr;
    if (((Nr = Sr = null), Fc(e), t)) for (e = 0; e < t.length; e++) Fc(t[e]);
  }
}
function Up(e, t) {
  return e(t);
}
function $p() {}
var oa = !1;
function Hp(e, t, n) {
  if (oa) return e(t, n);
  oa = !0;
  try {
    return Up(e, t, n);
  } finally {
    ((oa = !1), (Sr !== null || Nr !== null) && ($p(), Bp()));
  }
}
function Ri(e, t) {
  var n = e.stateNode;
  if (n === null) return null;
  var r = Pl(n);
  if (r === null) return null;
  n = r[t];
  e: switch (t) {
    case "onClick":
    case "onClickCapture":
    case "onDoubleClick":
    case "onDoubleClickCapture":
    case "onMouseDown":
    case "onMouseDownCapture":
    case "onMouseMove":
    case "onMouseMoveCapture":
    case "onMouseUp":
    case "onMouseUpCapture":
    case "onMouseEnter":
      ((r = !r.disabled) ||
        ((e = e.type),
        (r = !(
          e === "button" ||
          e === "input" ||
          e === "select" ||
          e === "textarea"
        ))),
        (e = !r));
      break e;
    default:
      e = !1;
  }
  if (e) return null;
  if (n && typeof n != "function") throw Error(P(231, t, typeof n));
  return n;
}
var ss = !1;
if (Qt)
  try {
    var ei = {};
    (Object.defineProperty(ei, "passive", {
      get: function () {
        ss = !0;
      },
    }),
      window.addEventListener("test", ei, ei),
      window.removeEventListener("test", ei, ei));
  } catch {
    ss = !1;
  }
function ub(e, t, n, r, i, o, l, a, s) {
  var u = Array.prototype.slice.call(arguments, 3);
  try {
    t.apply(n, u);
  } catch (d) {
    this.onError(d);
  }
}
var yi = !1,
  Jo = null,
  el = !1,
  us = null,
  cb = {
    onError: function (e) {
      ((yi = !0), (Jo = e));
    },
  };
function db(e, t, n, r, i, o, l, a, s) {
  ((yi = !1), (Jo = null), ub.apply(cb, arguments));
}
function fb(e, t, n, r, i, o, l, a, s) {
  if ((db.apply(this, arguments), yi)) {
    if (yi) {
      var u = Jo;
      ((yi = !1), (Jo = null));
    } else throw Error(P(198));
    el || ((el = !0), (us = u));
  }
}
function Jn(e) {
  var t = e,
    n = e;
  if (e.alternate) for (; t.return;) t = t.return;
  else {
    e = t;
    do ((t = e), t.flags & 4098 && (n = t.return), (e = t.return));
    while (e);
  }
  return t.tag === 3 ? n : null;
}
function jp(e) {
  if (e.tag === 13) {
    var t = e.memoizedState;
    if (
      (t === null && ((e = e.alternate), e !== null && (t = e.memoizedState)),
      t !== null)
    )
      return t.dehydrated;
  }
  return null;
}
function Bc(e) {
  if (Jn(e) !== e) throw Error(P(188));
}
function pb(e) {
  var t = e.alternate;
  if (!t) {
    if (((t = Jn(e)), t === null)) throw Error(P(188));
    return t !== e ? null : e;
  }
  for (var n = e, r = t; ;) {
    var i = n.return;
    if (i === null) break;
    var o = i.alternate;
    if (o === null) {
      if (((r = i.return), r !== null)) {
        n = r;
        continue;
      }
      break;
    }
    if (i.child === o.child) {
      for (o = i.child; o;) {
        if (o === n) return (Bc(i), e);
        if (o === r) return (Bc(i), t);
        o = o.sibling;
      }
      throw Error(P(188));
    }
    if (n.return !== r.return) ((n = i), (r = o));
    else {
      for (var l = !1, a = i.child; a;) {
        if (a === n) {
          ((l = !0), (n = i), (r = o));
          break;
        }
        if (a === r) {
          ((l = !0), (r = i), (n = o));
          break;
        }
        a = a.sibling;
      }
      if (!l) {
        for (a = o.child; a;) {
          if (a === n) {
            ((l = !0), (n = o), (r = i));
            break;
          }
          if (a === r) {
            ((l = !0), (r = o), (n = i));
            break;
          }
          a = a.sibling;
        }
        if (!l) throw Error(P(189));
      }
    }
    if (n.alternate !== r) throw Error(P(190));
  }
  if (n.tag !== 3) throw Error(P(188));
  return n.stateNode.current === n ? e : t;
}
function Wp(e) {
  return ((e = pb(e)), e !== null ? Gp(e) : null);
}
function Gp(e) {
  if (e.tag === 5 || e.tag === 6) return e;
  for (e = e.child; e !== null;) {
    var t = Gp(e);
    if (t !== null) return t;
    e = e.sibling;
  }
  return null;
}
var Kp = ut.unstable_scheduleCallback,
  Uc = ut.unstable_cancelCallback,
  hb = ut.unstable_shouldYield,
  gb = ut.unstable_requestPaint,
  _e = ut.unstable_now,
  mb = ut.unstable_getCurrentPriorityLevel,
  gu = ut.unstable_ImmediatePriority,
  Vp = ut.unstable_UserBlockingPriority,
  tl = ut.unstable_NormalPriority,
  yb = ut.unstable_LowPriority,
  qp = ut.unstable_IdlePriority,
  Il = null,
  zt = null;
function bb(e) {
  if (zt && typeof zt.onCommitFiberRoot == "function")
    try {
      zt.onCommitFiberRoot(Il, e, void 0, (e.current.flags & 128) === 128);
    } catch {}
}
var St = Math.clz32 ? Math.clz32 : wb,
  vb = Math.log,
  Eb = Math.LN2;
function wb(e) {
  return ((e >>>= 0), e === 0 ? 32 : (31 - ((vb(e) / Eb) | 0)) | 0);
}
var po = 64,
  ho = 4194304;
function hi(e) {
  switch (e & -e) {
    case 1:
      return 1;
    case 2:
      return 2;
    case 4:
      return 4;
    case 8:
      return 8;
    case 16:
      return 16;
    case 32:
      return 32;
    case 64:
    case 128:
    case 256:
    case 512:
    case 1024:
    case 2048:
    case 4096:
    case 8192:
    case 16384:
    case 32768:
    case 65536:
    case 131072:
    case 262144:
    case 524288:
    case 1048576:
    case 2097152:
      return e & 4194240;
    case 4194304:
    case 8388608:
    case 16777216:
    case 33554432:
    case 67108864:
      return e & 130023424;
    case 134217728:
      return 134217728;
    case 268435456:
      return 268435456;
    case 536870912:
      return 536870912;
    case 1073741824:
      return 1073741824;
    default:
      return e;
  }
}
function nl(e, t) {
  var n = e.pendingLanes;
  if (n === 0) return 0;
  var r = 0,
    i = e.suspendedLanes,
    o = e.pingedLanes,
    l = n & 268435455;
  if (l !== 0) {
    var a = l & ~i;
    a !== 0 ? (r = hi(a)) : ((o &= l), o !== 0 && (r = hi(o)));
  } else ((l = n & ~i), l !== 0 ? (r = hi(l)) : o !== 0 && (r = hi(o)));
  if (r === 0) return 0;
  if (
    t !== 0 &&
    t !== r &&
    !(t & i) &&
    ((i = r & -r), (o = t & -t), i >= o || (i === 16 && (o & 4194240) !== 0))
  )
    return t;
  if ((r & 4 && (r |= n & 16), (t = e.entangledLanes), t !== 0))
    for (e = e.entanglements, t &= r; 0 < t;)
      ((n = 31 - St(t)), (i = 1 << n), (r |= e[n]), (t &= ~i));
  return r;
}
function xb(e, t) {
  switch (e) {
    case 1:
    case 2:
    case 4:
      return t + 250;
    case 8:
    case 16:
    case 32:
    case 64:
    case 128:
    case 256:
    case 512:
    case 1024:
    case 2048:
    case 4096:
    case 8192:
    case 16384:
    case 32768:
    case 65536:
    case 131072:
    case 262144:
    case 524288:
    case 1048576:
    case 2097152:
      return t + 5e3;
    case 4194304:
    case 8388608:
    case 16777216:
    case 33554432:
    case 67108864:
      return -1;
    case 134217728:
    case 268435456:
    case 536870912:
    case 1073741824:
      return -1;
    default:
      return -1;
  }
}
function _b(e, t) {
  for (
    var n = e.suspendedLanes,
      r = e.pingedLanes,
      i = e.expirationTimes,
      o = e.pendingLanes;
    0 < o;
  ) {
    var l = 31 - St(o),
      a = 1 << l,
      s = i[l];
    (s === -1
      ? (!(a & n) || a & r) && (i[l] = xb(a, t))
      : s <= t && (e.expiredLanes |= a),
      (o &= ~a));
  }
}
function cs(e) {
  return (
    (e = e.pendingLanes & -1073741825),
    e !== 0 ? e : e & 1073741824 ? 1073741824 : 0
  );
}
function Yp() {
  var e = po;
  return ((po <<= 1), !(po & 4194240) && (po = 64), e);
}
function la(e) {
  for (var t = [], n = 0; 31 > n; n++) t.push(e);
  return t;
}
function Xi(e, t, n) {
  ((e.pendingLanes |= t),
    t !== 536870912 && ((e.suspendedLanes = 0), (e.pingedLanes = 0)),
    (e = e.eventTimes),
    (t = 31 - St(t)),
    (e[t] = n));
}
function kb(e, t) {
  var n = e.pendingLanes & ~t;
  ((e.pendingLanes = t),
    (e.suspendedLanes = 0),
    (e.pingedLanes = 0),
    (e.expiredLanes &= t),
    (e.mutableReadLanes &= t),
    (e.entangledLanes &= t),
    (t = e.entanglements));
  var r = e.eventTimes;
  for (e = e.expirationTimes; 0 < n;) {
    var i = 31 - St(n),
      o = 1 << i;
    ((t[i] = 0), (r[i] = -1), (e[i] = -1), (n &= ~o));
  }
}
function mu(e, t) {
  var n = (e.entangledLanes |= t);
  for (e = e.entanglements; n;) {
    var r = 31 - St(n),
      i = 1 << r;
    ((i & t) | (e[r] & t) && (e[r] |= t), (n &= ~i));
  }
}
var ae = 0;
function Qp(e) {
  return (
    (e &= -e),
    1 < e ? (4 < e ? (e & 268435455 ? 16 : 536870912) : 4) : 1
  );
}
var Zp,
  yu,
  Xp,
  Jp,
  eh,
  ds = !1,
  go = [],
  bn = null,
  vn = null,
  En = null,
  Oi = new Map(),
  Ii = new Map(),
  fn = [],
  Sb =
    "mousedown mouseup touchcancel touchend touchstart auxclick dblclick pointercancel pointerdown pointerup dragend dragstart drop compositionend compositionstart keydown keypress keyup input textInput copy cut paste click change contextmenu reset submit".split(
      " ",
    );
function $c(e, t) {
  switch (e) {
    case "focusin":
    case "focusout":
      bn = null;
      break;
    case "dragenter":
    case "dragleave":
      vn = null;
      break;
    case "mouseover":
    case "mouseout":
      En = null;
      break;
    case "pointerover":
    case "pointerout":
      Oi.delete(t.pointerId);
      break;
    case "gotpointercapture":
    case "lostpointercapture":
      Ii.delete(t.pointerId);
  }
}
function ti(e, t, n, r, i, o) {
  return e === null || e.nativeEvent !== o
    ? ((e = {
        blockedOn: t,
        domEventName: n,
        eventSystemFlags: r,
        nativeEvent: o,
        targetContainers: [i],
      }),
      t !== null && ((t = eo(t)), t !== null && yu(t)),
      e)
    : ((e.eventSystemFlags |= r),
      (t = e.targetContainers),
      i !== null && t.indexOf(i) === -1 && t.push(i),
      e);
}
function Nb(e, t, n, r, i) {
  switch (t) {
    case "focusin":
      return ((bn = ti(bn, e, t, n, r, i)), !0);
    case "dragenter":
      return ((vn = ti(vn, e, t, n, r, i)), !0);
    case "mouseover":
      return ((En = ti(En, e, t, n, r, i)), !0);
    case "pointerover":
      var o = i.pointerId;
      return (Oi.set(o, ti(Oi.get(o) || null, e, t, n, r, i)), !0);
    case "gotpointercapture":
      return (
        (o = i.pointerId),
        Ii.set(o, ti(Ii.get(o) || null, e, t, n, r, i)),
        !0
      );
  }
  return !1;
}
function th(e) {
  var t = Fn(e.target);
  if (t !== null) {
    var n = Jn(t);
    if (n !== null) {
      if (((t = n.tag), t === 13)) {
        if (((t = jp(n)), t !== null)) {
          ((e.blockedOn = t),
            eh(e.priority, function () {
              Xp(n);
            }));
          return;
        }
      } else if (t === 3 && n.stateNode.current.memoizedState.isDehydrated) {
        e.blockedOn = n.tag === 3 ? n.stateNode.containerInfo : null;
        return;
      }
    }
  }
  e.blockedOn = null;
}
function Fo(e) {
  if (e.blockedOn !== null) return !1;
  for (var t = e.targetContainers; 0 < t.length;) {
    var n = fs(e.domEventName, e.eventSystemFlags, t[0], e.nativeEvent);
    if (n === null) {
      n = e.nativeEvent;
      var r = new n.constructor(n.type, n);
      ((ls = r), n.target.dispatchEvent(r), (ls = null));
    } else return ((t = eo(n)), t !== null && yu(t), (e.blockedOn = n), !1);
    t.shift();
  }
  return !0;
}
function Hc(e, t, n) {
  Fo(e) && n.delete(t);
}
function Cb() {
  ((ds = !1),
    bn !== null && Fo(bn) && (bn = null),
    vn !== null && Fo(vn) && (vn = null),
    En !== null && Fo(En) && (En = null),
    Oi.forEach(Hc),
    Ii.forEach(Hc));
}
function ni(e, t) {
  e.blockedOn === t &&
    ((e.blockedOn = null),
    ds ||
      ((ds = !0),
      ut.unstable_scheduleCallback(ut.unstable_NormalPriority, Cb)));
}
function Mi(e) {
  function t(i) {
    return ni(i, e);
  }
  if (0 < go.length) {
    ni(go[0], e);
    for (var n = 1; n < go.length; n++) {
      var r = go[n];
      r.blockedOn === e && (r.blockedOn = null);
    }
  }
  for (
    bn !== null && ni(bn, e),
      vn !== null && ni(vn, e),
      En !== null && ni(En, e),
      Oi.forEach(t),
      Ii.forEach(t),
      n = 0;
    n < fn.length;
    n++
  )
    ((r = fn[n]), r.blockedOn === e && (r.blockedOn = null));
  for (; 0 < fn.length && ((n = fn[0]), n.blockedOn === null);)
    (th(n), n.blockedOn === null && fn.shift());
}
var Cr = en.ReactCurrentBatchConfig,
  rl = !0;
function Tb(e, t, n, r) {
  var i = ae,
    o = Cr.transition;
  Cr.transition = null;
  try {
    ((ae = 1), bu(e, t, n, r));
  } finally {
    ((ae = i), (Cr.transition = o));
  }
}
function Ab(e, t, n, r) {
  var i = ae,
    o = Cr.transition;
  Cr.transition = null;
  try {
    ((ae = 4), bu(e, t, n, r));
  } finally {
    ((ae = i), (Cr.transition = o));
  }
}
function bu(e, t, n, r) {
  if (rl) {
    var i = fs(e, t, n, r);
    if (i === null) (ma(e, t, r, il, n), $c(e, r));
    else if (Nb(i, e, t, n, r)) r.stopPropagation();
    else if (($c(e, r), t & 4 && -1 < Sb.indexOf(e))) {
      for (; i !== null;) {
        var o = eo(i);
        if (
          (o !== null && Zp(o),
          (o = fs(e, t, n, r)),
          o === null && ma(e, t, r, il, n),
          o === i)
        )
          break;
        i = o;
      }
      i !== null && r.stopPropagation();
    } else ma(e, t, r, null, n);
  }
}
var il = null;
function fs(e, t, n, r) {
  if (((il = null), (e = hu(r)), (e = Fn(e)), e !== null))
    if (((t = Jn(e)), t === null)) e = null;
    else if (((n = t.tag), n === 13)) {
      if (((e = jp(t)), e !== null)) return e;
      e = null;
    } else if (n === 3) {
      if (t.stateNode.current.memoizedState.isDehydrated)
        return t.tag === 3 ? t.stateNode.containerInfo : null;
      e = null;
    } else t !== e && (e = null);
  return ((il = e), null);
}
function nh(e) {
  switch (e) {
    case "cancel":
    case "click":
    case "close":
    case "contextmenu":
    case "copy":
    case "cut":
    case "auxclick":
    case "dblclick":
    case "dragend":
    case "dragstart":
    case "drop":
    case "focusin":
    case "focusout":
    case "input":
    case "invalid":
    case "keydown":
    case "keypress":
    case "keyup":
    case "mousedown":
    case "mouseup":
    case "paste":
    case "pause":
    case "play":
    case "pointercancel":
    case "pointerdown":
    case "pointerup":
    case "ratechange":
    case "reset":
    case "resize":
    case "seeked":
    case "submit":
    case "touchcancel":
    case "touchend":
    case "touchstart":
    case "volumechange":
    case "change":
    case "selectionchange":
    case "textInput":
    case "compositionstart":
    case "compositionend":
    case "compositionupdate":
    case "beforeblur":
    case "afterblur":
    case "beforeinput":
    case "blur":
    case "fullscreenchange":
    case "focus":
    case "hashchange":
    case "popstate":
    case "select":
    case "selectstart":
      return 1;
    case "drag":
    case "dragenter":
    case "dragexit":
    case "dragleave":
    case "dragover":
    case "mousemove":
    case "mouseout":
    case "mouseover":
    case "pointermove":
    case "pointerout":
    case "pointerover":
    case "scroll":
    case "toggle":
    case "touchmove":
    case "wheel":
    case "mouseenter":
    case "mouseleave":
    case "pointerenter":
    case "pointerleave":
      return 4;
    case "message":
      switch (mb()) {
        case gu:
          return 1;
        case Vp:
          return 4;
        case tl:
        case yb:
          return 16;
        case qp:
          return 536870912;
        default:
          return 16;
      }
    default:
      return 16;
  }
}
var hn = null,
  vu = null,
  Bo = null;
function rh() {
  if (Bo) return Bo;
  var e,
    t = vu,
    n = t.length,
    r,
    i = "value" in hn ? hn.value : hn.textContent,
    o = i.length;
  for (e = 0; e < n && t[e] === i[e]; e++);
  var l = n - e;
  for (r = 1; r <= l && t[n - r] === i[o - r]; r++);
  return (Bo = i.slice(e, 1 < r ? 1 - r : void 0));
}
function Uo(e) {
  var t = e.keyCode;
  return (
    "charCode" in e
      ? ((e = e.charCode), e === 0 && t === 13 && (e = 13))
      : (e = t),
    e === 10 && (e = 13),
    32 <= e || e === 13 ? e : 0
  );
}
function mo() {
  return !0;
}
function jc() {
  return !1;
}
function dt(e) {
  function t(n, r, i, o, l) {
    ((this._reactName = n),
      (this._targetInst = i),
      (this.type = r),
      (this.nativeEvent = o),
      (this.target = l),
      (this.currentTarget = null));
    for (var a in e)
      e.hasOwnProperty(a) && ((n = e[a]), (this[a] = n ? n(o) : o[a]));
    return (
      (this.isDefaultPrevented = (
        o.defaultPrevented != null ? o.defaultPrevented : o.returnValue === !1
      )
        ? mo
        : jc),
      (this.isPropagationStopped = jc),
      this
    );
  }
  return (
    Ee(t.prototype, {
      preventDefault: function () {
        this.defaultPrevented = !0;
        var n = this.nativeEvent;
        n &&
          (n.preventDefault
            ? n.preventDefault()
            : typeof n.returnValue != "unknown" && (n.returnValue = !1),
          (this.isDefaultPrevented = mo));
      },
      stopPropagation: function () {
        var n = this.nativeEvent;
        n &&
          (n.stopPropagation
            ? n.stopPropagation()
            : typeof n.cancelBubble != "unknown" && (n.cancelBubble = !0),
          (this.isPropagationStopped = mo));
      },
      persist: function () {},
      isPersistent: mo,
    }),
    t
  );
}
var Hr = {
    eventPhase: 0,
    bubbles: 0,
    cancelable: 0,
    timeStamp: function (e) {
      return e.timeStamp || Date.now();
    },
    defaultPrevented: 0,
    isTrusted: 0,
  },
  Eu = dt(Hr),
  Ji = Ee({}, Hr, { view: 0, detail: 0 }),
  Rb = dt(Ji),
  aa,
  sa,
  ri,
  Ml = Ee({}, Ji, {
    screenX: 0,
    screenY: 0,
    clientX: 0,
    clientY: 0,
    pageX: 0,
    pageY: 0,
    ctrlKey: 0,
    shiftKey: 0,
    altKey: 0,
    metaKey: 0,
    getModifierState: wu,
    button: 0,
    buttons: 0,
    relatedTarget: function (e) {
      return e.relatedTarget === void 0
        ? e.fromElement === e.srcElement
          ? e.toElement
          : e.fromElement
        : e.relatedTarget;
    },
    movementX: function (e) {
      return "movementX" in e
        ? e.movementX
        : (e !== ri &&
            (ri && e.type === "mousemove"
              ? ((aa = e.screenX - ri.screenX), (sa = e.screenY - ri.screenY))
              : (sa = aa = 0),
            (ri = e)),
          aa);
    },
    movementY: function (e) {
      return "movementY" in e ? e.movementY : sa;
    },
  }),
  Wc = dt(Ml),
  Ob = Ee({}, Ml, { dataTransfer: 0 }),
  Ib = dt(Ob),
  Mb = Ee({}, Ji, { relatedTarget: 0 }),
  ua = dt(Mb),
  Lb = Ee({}, Hr, { animationName: 0, elapsedTime: 0, pseudoElement: 0 }),
  Db = dt(Lb),
  Pb = Ee({}, Hr, {
    clipboardData: function (e) {
      return "clipboardData" in e ? e.clipboardData : window.clipboardData;
    },
  }),
  zb = dt(Pb),
  Fb = Ee({}, Hr, { data: 0 }),
  Gc = dt(Fb),
  Bb = {
    Esc: "Escape",
    Spacebar: " ",
    Left: "ArrowLeft",
    Up: "ArrowUp",
    Right: "ArrowRight",
    Down: "ArrowDown",
    Del: "Delete",
    Win: "OS",
    Menu: "ContextMenu",
    Apps: "ContextMenu",
    Scroll: "ScrollLock",
    MozPrintableKey: "Unidentified",
  },
  Ub = {
    8: "Backspace",
    9: "Tab",
    12: "Clear",
    13: "Enter",
    16: "Shift",
    17: "Control",
    18: "Alt",
    19: "Pause",
    20: "CapsLock",
    27: "Escape",
    32: " ",
    33: "PageUp",
    34: "PageDown",
    35: "End",
    36: "Home",
    37: "ArrowLeft",
    38: "ArrowUp",
    39: "ArrowRight",
    40: "ArrowDown",
    45: "Insert",
    46: "Delete",
    112: "F1",
    113: "F2",
    114: "F3",
    115: "F4",
    116: "F5",
    117: "F6",
    118: "F7",
    119: "F8",
    120: "F9",
    121: "F10",
    122: "F11",
    123: "F12",
    144: "NumLock",
    145: "ScrollLock",
    224: "Meta",
  },
  $b = {
    Alt: "altKey",
    Control: "ctrlKey",
    Meta: "metaKey",
    Shift: "shiftKey",
  };
function Hb(e) {
  var t = this.nativeEvent;
  return t.getModifierState ? t.getModifierState(e) : (e = $b[e]) ? !!t[e] : !1;
}
function wu() {
  return Hb;
}
var jb = Ee({}, Ji, {
    key: function (e) {
      if (e.key) {
        var t = Bb[e.key] || e.key;
        if (t !== "Unidentified") return t;
      }
      return e.type === "keypress"
        ? ((e = Uo(e)), e === 13 ? "Enter" : String.fromCharCode(e))
        : e.type === "keydown" || e.type === "keyup"
          ? Ub[e.keyCode] || "Unidentified"
          : "";
    },
    code: 0,
    location: 0,
    ctrlKey: 0,
    shiftKey: 0,
    altKey: 0,
    metaKey: 0,
    repeat: 0,
    locale: 0,
    getModifierState: wu,
    charCode: function (e) {
      return e.type === "keypress" ? Uo(e) : 0;
    },
    keyCode: function (e) {
      return e.type === "keydown" || e.type === "keyup" ? e.keyCode : 0;
    },
    which: function (e) {
      return e.type === "keypress"
        ? Uo(e)
        : e.type === "keydown" || e.type === "keyup"
          ? e.keyCode
          : 0;
    },
  }),
  Wb = dt(jb),
  Gb = Ee({}, Ml, {
    pointerId: 0,
    width: 0,
    height: 0,
    pressure: 0,
    tangentialPressure: 0,
    tiltX: 0,
    tiltY: 0,
    twist: 0,
    pointerType: 0,
    isPrimary: 0,
  }),
  Kc = dt(Gb),
  Kb = Ee({}, Ji, {
    touches: 0,
    targetTouches: 0,
    changedTouches: 0,
    altKey: 0,
    metaKey: 0,
    ctrlKey: 0,
    shiftKey: 0,
    getModifierState: wu,
  }),
  Vb = dt(Kb),
  qb = Ee({}, Hr, { propertyName: 0, elapsedTime: 0, pseudoElement: 0 }),
  Yb = dt(qb),
  Qb = Ee({}, Ml, {
    deltaX: function (e) {
      return "deltaX" in e ? e.deltaX : "wheelDeltaX" in e ? -e.wheelDeltaX : 0;
    },
    deltaY: function (e) {
      return "deltaY" in e
        ? e.deltaY
        : "wheelDeltaY" in e
          ? -e.wheelDeltaY
          : "wheelDelta" in e
            ? -e.wheelDelta
            : 0;
    },
    deltaZ: 0,
    deltaMode: 0,
  }),
  Zb = dt(Qb),
  Xb = [9, 13, 27, 32],
  xu = Qt && "CompositionEvent" in window,
  bi = null;
Qt && "documentMode" in document && (bi = document.documentMode);
var Jb = Qt && "TextEvent" in window && !bi,
  ih = Qt && (!xu || (bi && 8 < bi && 11 >= bi)),
  Vc = " ",
  qc = !1;
function oh(e, t) {
  switch (e) {
    case "keyup":
      return Xb.indexOf(t.keyCode) !== -1;
    case "keydown":
      return t.keyCode !== 229;
    case "keypress":
    case "mousedown":
    case "focusout":
      return !0;
    default:
      return !1;
  }
}
function lh(e) {
  return ((e = e.detail), typeof e == "object" && "data" in e ? e.data : null);
}
var hr = !1;
function ev(e, t) {
  switch (e) {
    case "compositionend":
      return lh(t);
    case "keypress":
      return t.which !== 32 ? null : ((qc = !0), Vc);
    case "textInput":
      return ((e = t.data), e === Vc && qc ? null : e);
    default:
      return null;
  }
}
function tv(e, t) {
  if (hr)
    return e === "compositionend" || (!xu && oh(e, t))
      ? ((e = rh()), (Bo = vu = hn = null), (hr = !1), e)
      : null;
  switch (e) {
    case "paste":
      return null;
    case "keypress":
      if (!(t.ctrlKey || t.altKey || t.metaKey) || (t.ctrlKey && t.altKey)) {
        if (t.char && 1 < t.char.length) return t.char;
        if (t.which) return String.fromCharCode(t.which);
      }
      return null;
    case "compositionend":
      return ih && t.locale !== "ko" ? null : t.data;
    default:
      return null;
  }
}
var nv = {
  color: !0,
  date: !0,
  datetime: !0,
  "datetime-local": !0,
  email: !0,
  month: !0,
  number: !0,
  password: !0,
  range: !0,
  search: !0,
  tel: !0,
  text: !0,
  time: !0,
  url: !0,
  week: !0,
};
function Yc(e) {
  var t = e && e.nodeName && e.nodeName.toLowerCase();
  return t === "input" ? !!nv[e.type] : t === "textarea";
}
function ah(e, t, n, r) {
  (Fp(r),
    (t = ol(t, "onChange")),
    0 < t.length &&
      ((n = new Eu("onChange", "change", null, n, r)),
      e.push({ event: n, listeners: t })));
}
var vi = null,
  Li = null;
function rv(e) {
  bh(e, 0);
}
function Ll(e) {
  var t = yr(e);
  if (Op(t)) return e;
}
function iv(e, t) {
  if (e === "change") return t;
}
var sh = !1;
if (Qt) {
  var ca;
  if (Qt) {
    var da = "oninput" in document;
    if (!da) {
      var Qc = document.createElement("div");
      (Qc.setAttribute("oninput", "return;"),
        (da = typeof Qc.oninput == "function"));
    }
    ca = da;
  } else ca = !1;
  sh = ca && (!document.documentMode || 9 < document.documentMode);
}
function Zc() {
  vi && (vi.detachEvent("onpropertychange", uh), (Li = vi = null));
}
function uh(e) {
  if (e.propertyName === "value" && Ll(Li)) {
    var t = [];
    (ah(t, Li, e, hu(e)), Hp(rv, t));
  }
}
function ov(e, t, n) {
  e === "focusin"
    ? (Zc(), (vi = t), (Li = n), vi.attachEvent("onpropertychange", uh))
    : e === "focusout" && Zc();
}
function lv(e) {
  if (e === "selectionchange" || e === "keyup" || e === "keydown")
    return Ll(Li);
}
function av(e, t) {
  if (e === "click") return Ll(t);
}
function sv(e, t) {
  if (e === "input" || e === "change") return Ll(t);
}
function uv(e, t) {
  return (e === t && (e !== 0 || 1 / e === 1 / t)) || (e !== e && t !== t);
}
var Tt = typeof Object.is == "function" ? Object.is : uv;
function Di(e, t) {
  if (Tt(e, t)) return !0;
  if (typeof e != "object" || e === null || typeof t != "object" || t === null)
    return !1;
  var n = Object.keys(e),
    r = Object.keys(t);
  if (n.length !== r.length) return !1;
  for (r = 0; r < n.length; r++) {
    var i = n[r];
    if (!qa.call(t, i) || !Tt(e[i], t[i])) return !1;
  }
  return !0;
}
function Xc(e) {
  for (; e && e.firstChild;) e = e.firstChild;
  return e;
}
function Jc(e, t) {
  var n = Xc(e);
  e = 0;
  for (var r; n;) {
    if (n.nodeType === 3) {
      if (((r = e + n.textContent.length), e <= t && r >= t))
        return { node: n, offset: t - e };
      e = r;
    }
    e: {
      for (; n;) {
        if (n.nextSibling) {
          n = n.nextSibling;
          break e;
        }
        n = n.parentNode;
      }
      n = void 0;
    }
    n = Xc(n);
  }
}
function ch(e, t) {
  return e && t
    ? e === t
      ? !0
      : e && e.nodeType === 3
        ? !1
        : t && t.nodeType === 3
          ? ch(e, t.parentNode)
          : "contains" in e
            ? e.contains(t)
            : e.compareDocumentPosition
              ? !!(e.compareDocumentPosition(t) & 16)
              : !1
    : !1;
}
function dh() {
  for (var e = window, t = Xo(); t instanceof e.HTMLIFrameElement;) {
    try {
      var n = typeof t.contentWindow.location.href == "string";
    } catch {
      n = !1;
    }
    if (n) e = t.contentWindow;
    else break;
    t = Xo(e.document);
  }
  return t;
}
function _u(e) {
  var t = e && e.nodeName && e.nodeName.toLowerCase();
  return (
    t &&
    ((t === "input" &&
      (e.type === "text" ||
        e.type === "search" ||
        e.type === "tel" ||
        e.type === "url" ||
        e.type === "password")) ||
      t === "textarea" ||
      e.contentEditable === "true")
  );
}
function cv(e) {
  var t = dh(),
    n = e.focusedElem,
    r = e.selectionRange;
  if (
    t !== n &&
    n &&
    n.ownerDocument &&
    ch(n.ownerDocument.documentElement, n)
  ) {
    if (r !== null && _u(n)) {
      if (
        ((t = r.start),
        (e = r.end),
        e === void 0 && (e = t),
        "selectionStart" in n)
      )
        ((n.selectionStart = t),
          (n.selectionEnd = Math.min(e, n.value.length)));
      else if (
        ((e = ((t = n.ownerDocument || document) && t.defaultView) || window),
        e.getSelection)
      ) {
        e = e.getSelection();
        var i = n.textContent.length,
          o = Math.min(r.start, i);
        ((r = r.end === void 0 ? o : Math.min(r.end, i)),
          !e.extend && o > r && ((i = r), (r = o), (o = i)),
          (i = Jc(n, o)));
        var l = Jc(n, r);
        i &&
          l &&
          (e.rangeCount !== 1 ||
            e.anchorNode !== i.node ||
            e.anchorOffset !== i.offset ||
            e.focusNode !== l.node ||
            e.focusOffset !== l.offset) &&
          ((t = t.createRange()),
          t.setStart(i.node, i.offset),
          e.removeAllRanges(),
          o > r
            ? (e.addRange(t), e.extend(l.node, l.offset))
            : (t.setEnd(l.node, l.offset), e.addRange(t)));
      }
    }
    for (t = [], e = n; (e = e.parentNode);)
      e.nodeType === 1 &&
        t.push({ element: e, left: e.scrollLeft, top: e.scrollTop });
    for (typeof n.focus == "function" && n.focus(), n = 0; n < t.length; n++)
      ((e = t[n]),
        (e.element.scrollLeft = e.left),
        (e.element.scrollTop = e.top));
  }
}
var dv = Qt && "documentMode" in document && 11 >= document.documentMode,
  gr = null,
  ps = null,
  Ei = null,
  hs = !1;
function ed(e, t, n) {
  var r = n.window === n ? n.document : n.nodeType === 9 ? n : n.ownerDocument;
  hs ||
    gr == null ||
    gr !== Xo(r) ||
    ((r = gr),
    "selectionStart" in r && _u(r)
      ? (r = { start: r.selectionStart, end: r.selectionEnd })
      : ((r = (
          (r.ownerDocument && r.ownerDocument.defaultView) ||
          window
        ).getSelection()),
        (r = {
          anchorNode: r.anchorNode,
          anchorOffset: r.anchorOffset,
          focusNode: r.focusNode,
          focusOffset: r.focusOffset,
        })),
    (Ei && Di(Ei, r)) ||
      ((Ei = r),
      (r = ol(ps, "onSelect")),
      0 < r.length &&
        ((t = new Eu("onSelect", "select", null, t, n)),
        e.push({ event: t, listeners: r }),
        (t.target = gr))));
}
function yo(e, t) {
  var n = {};
  return (
    (n[e.toLowerCase()] = t.toLowerCase()),
    (n["Webkit" + e] = "webkit" + t),
    (n["Moz" + e] = "moz" + t),
    n
  );
}
var mr = {
    animationend: yo("Animation", "AnimationEnd"),
    animationiteration: yo("Animation", "AnimationIteration"),
    animationstart: yo("Animation", "AnimationStart"),
    transitionend: yo("Transition", "TransitionEnd"),
  },
  fa = {},
  fh = {};
Qt &&
  ((fh = document.createElement("div").style),
  "AnimationEvent" in window ||
    (delete mr.animationend.animation,
    delete mr.animationiteration.animation,
    delete mr.animationstart.animation),
  "TransitionEvent" in window || delete mr.transitionend.transition);
function Dl(e) {
  if (fa[e]) return fa[e];
  if (!mr[e]) return e;
  var t = mr[e],
    n;
  for (n in t) if (t.hasOwnProperty(n) && n in fh) return (fa[e] = t[n]);
  return e;
}
var ph = Dl("animationend"),
  hh = Dl("animationiteration"),
  gh = Dl("animationstart"),
  mh = Dl("transitionend"),
  yh = new Map(),
  td =
    "abort auxClick cancel canPlay canPlayThrough click close contextMenu copy cut drag dragEnd dragEnter dragExit dragLeave dragOver dragStart drop durationChange emptied encrypted ended error gotPointerCapture input invalid keyDown keyPress keyUp load loadedData loadedMetadata loadStart lostPointerCapture mouseDown mouseMove mouseOut mouseOver mouseUp paste pause play playing pointerCancel pointerDown pointerMove pointerOut pointerOver pointerUp progress rateChange reset resize seeked seeking stalled submit suspend timeUpdate touchCancel touchEnd touchStart volumeChange scroll toggle touchMove waiting wheel".split(
      " ",
    );
function Tn(e, t) {
  (yh.set(e, t), Xn(t, [e]));
}
for (var pa = 0; pa < td.length; pa++) {
  var ha = td[pa],
    fv = ha.toLowerCase(),
    pv = ha[0].toUpperCase() + ha.slice(1);
  Tn(fv, "on" + pv);
}
Tn(ph, "onAnimationEnd");
Tn(hh, "onAnimationIteration");
Tn(gh, "onAnimationStart");
Tn("dblclick", "onDoubleClick");
Tn("focusin", "onFocus");
Tn("focusout", "onBlur");
Tn(mh, "onTransitionEnd");
Ir("onMouseEnter", ["mouseout", "mouseover"]);
Ir("onMouseLeave", ["mouseout", "mouseover"]);
Ir("onPointerEnter", ["pointerout", "pointerover"]);
Ir("onPointerLeave", ["pointerout", "pointerover"]);
Xn(
  "onChange",
  "change click focusin focusout input keydown keyup selectionchange".split(
    " ",
  ),
);
Xn(
  "onSelect",
  "focusout contextmenu dragend focusin keydown keyup mousedown mouseup selectionchange".split(
    " ",
  ),
);
Xn("onBeforeInput", ["compositionend", "keypress", "textInput", "paste"]);
Xn(
  "onCompositionEnd",
  "compositionend focusout keydown keypress keyup mousedown".split(" "),
);
Xn(
  "onCompositionStart",
  "compositionstart focusout keydown keypress keyup mousedown".split(" "),
);
Xn(
  "onCompositionUpdate",
  "compositionupdate focusout keydown keypress keyup mousedown".split(" "),
);
var gi =
    "abort canplay canplaythrough durationchange emptied encrypted ended error loadeddata loadedmetadata loadstart pause play playing progress ratechange resize seeked seeking stalled suspend timeupdate volumechange waiting".split(
      " ",
    ),
  hv = new Set("cancel close invalid load scroll toggle".split(" ").concat(gi));
function nd(e, t, n) {
  var r = e.type || "unknown-event";
  ((e.currentTarget = n), fb(r, t, void 0, e), (e.currentTarget = null));
}
function bh(e, t) {
  t = (t & 4) !== 0;
  for (var n = 0; n < e.length; n++) {
    var r = e[n],
      i = r.event;
    r = r.listeners;
    e: {
      var o = void 0;
      if (t)
        for (var l = r.length - 1; 0 <= l; l--) {
          var a = r[l],
            s = a.instance,
            u = a.currentTarget;
          if (((a = a.listener), s !== o && i.isPropagationStopped())) break e;
          (nd(i, a, u), (o = s));
        }
      else
        for (l = 0; l < r.length; l++) {
          if (
            ((a = r[l]),
            (s = a.instance),
            (u = a.currentTarget),
            (a = a.listener),
            s !== o && i.isPropagationStopped())
          )
            break e;
          (nd(i, a, u), (o = s));
        }
    }
  }
  if (el) throw ((e = us), (el = !1), (us = null), e);
}
function ge(e, t) {
  var n = t[vs];
  n === void 0 && (n = t[vs] = new Set());
  var r = e + "__bubble";
  n.has(r) || (vh(t, e, 2, !1), n.add(r));
}
function ga(e, t, n) {
  var r = 0;
  (t && (r |= 4), vh(n, e, r, t));
}
var bo = "_reactListening" + Math.random().toString(36).slice(2);
function Pi(e) {
  if (!e[bo]) {
    ((e[bo] = !0),
      Np.forEach(function (n) {
        n !== "selectionchange" && (hv.has(n) || ga(n, !1, e), ga(n, !0, e));
      }));
    var t = e.nodeType === 9 ? e : e.ownerDocument;
    t === null || t[bo] || ((t[bo] = !0), ga("selectionchange", !1, t));
  }
}
function vh(e, t, n, r) {
  switch (nh(t)) {
    case 1:
      var i = Tb;
      break;
    case 4:
      i = Ab;
      break;
    default:
      i = bu;
  }
  ((n = i.bind(null, t, n, e)),
    (i = void 0),
    !ss ||
      (t !== "touchstart" && t !== "touchmove" && t !== "wheel") ||
      (i = !0),
    r
      ? i !== void 0
        ? e.addEventListener(t, n, { capture: !0, passive: i })
        : e.addEventListener(t, n, !0)
      : i !== void 0
        ? e.addEventListener(t, n, { passive: i })
        : e.addEventListener(t, n, !1));
}
function ma(e, t, n, r, i) {
  var o = r;
  if (!(t & 1) && !(t & 2) && r !== null)
    e: for (;;) {
      if (r === null) return;
      var l = r.tag;
      if (l === 3 || l === 4) {
        var a = r.stateNode.containerInfo;
        if (a === i || (a.nodeType === 8 && a.parentNode === i)) break;
        if (l === 4)
          for (l = r.return; l !== null;) {
            var s = l.tag;
            if (
              (s === 3 || s === 4) &&
              ((s = l.stateNode.containerInfo),
              s === i || (s.nodeType === 8 && s.parentNode === i))
            )
              return;
            l = l.return;
          }
        for (; a !== null;) {
          if (((l = Fn(a)), l === null)) return;
          if (((s = l.tag), s === 5 || s === 6)) {
            r = o = l;
            continue e;
          }
          a = a.parentNode;
        }
      }
      r = r.return;
    }
  Hp(function () {
    var u = o,
      d = hu(n),
      c = [];
    e: {
      var f = yh.get(e);
      if (f !== void 0) {
        var p = Eu,
          g = e;
        switch (e) {
          case "keypress":
            if (Uo(n) === 0) break e;
          case "keydown":
          case "keyup":
            p = Wb;
            break;
          case "focusin":
            ((g = "focus"), (p = ua));
            break;
          case "focusout":
            ((g = "blur"), (p = ua));
            break;
          case "beforeblur":
          case "afterblur":
            p = ua;
            break;
          case "click":
            if (n.button === 2) break e;
          case "auxclick":
          case "dblclick":
          case "mousedown":
          case "mousemove":
          case "mouseup":
          case "mouseout":
          case "mouseover":
          case "contextmenu":
            p = Wc;
            break;
          case "drag":
          case "dragend":
          case "dragenter":
          case "dragexit":
          case "dragleave":
          case "dragover":
          case "dragstart":
          case "drop":
            p = Ib;
            break;
          case "touchcancel":
          case "touchend":
          case "touchmove":
          case "touchstart":
            p = Vb;
            break;
          case ph:
          case hh:
          case gh:
            p = Db;
            break;
          case mh:
            p = Yb;
            break;
          case "scroll":
            p = Rb;
            break;
          case "wheel":
            p = Zb;
            break;
          case "copy":
          case "cut":
          case "paste":
            p = zb;
            break;
          case "gotpointercapture":
          case "lostpointercapture":
          case "pointercancel":
          case "pointerdown":
          case "pointermove":
          case "pointerout":
          case "pointerover":
          case "pointerup":
            p = Kc;
        }
        var y = (t & 4) !== 0,
          E = !y && e === "scroll",
          h = y ? (f !== null ? f + "Capture" : null) : f;
        y = [];
        for (var m = u, b; m !== null;) {
          b = m;
          var _ = b.stateNode;
          if (
            (b.tag === 5 &&
              _ !== null &&
              ((b = _),
              h !== null && ((_ = Ri(m, h)), _ != null && y.push(zi(m, _, b)))),
            E)
          )
            break;
          m = m.return;
        }
        0 < y.length &&
          ((f = new p(f, g, null, n, d)), c.push({ event: f, listeners: y }));
      }
    }
    if (!(t & 7)) {
      e: {
        if (
          ((f = e === "mouseover" || e === "pointerover"),
          (p = e === "mouseout" || e === "pointerout"),
          f &&
            n !== ls &&
            (g = n.relatedTarget || n.fromElement) &&
            (Fn(g) || g[Zt]))
        )
          break e;
        if (
          (p || f) &&
          ((f =
            d.window === d
              ? d
              : (f = d.ownerDocument)
                ? f.defaultView || f.parentWindow
                : window),
          p
            ? ((g = n.relatedTarget || n.toElement),
              (p = u),
              (g = g ? Fn(g) : null),
              g !== null &&
                ((E = Jn(g)), g !== E || (g.tag !== 5 && g.tag !== 6)) &&
                (g = null))
            : ((p = null), (g = u)),
          p !== g)
        ) {
          if (
            ((y = Wc),
            (_ = "onMouseLeave"),
            (h = "onMouseEnter"),
            (m = "mouse"),
            (e === "pointerout" || e === "pointerover") &&
              ((y = Kc),
              (_ = "onPointerLeave"),
              (h = "onPointerEnter"),
              (m = "pointer")),
            (E = p == null ? f : yr(p)),
            (b = g == null ? f : yr(g)),
            (f = new y(_, m + "leave", p, n, d)),
            (f.target = E),
            (f.relatedTarget = b),
            (_ = null),
            Fn(d) === u &&
              ((y = new y(h, m + "enter", g, n, d)),
              (y.target = b),
              (y.relatedTarget = E),
              (_ = y)),
            (E = _),
            p && g)
          )
            t: {
              for (y = p, h = g, m = 0, b = y; b; b = ar(b)) m++;
              for (b = 0, _ = h; _; _ = ar(_)) b++;
              for (; 0 < m - b;) ((y = ar(y)), m--);
              for (; 0 < b - m;) ((h = ar(h)), b--);
              for (; m--;) {
                if (y === h || (h !== null && y === h.alternate)) break t;
                ((y = ar(y)), (h = ar(h)));
              }
              y = null;
            }
          else y = null;
          (p !== null && rd(c, f, p, y, !1),
            g !== null && E !== null && rd(c, E, g, y, !0));
        }
      }
      e: {
        if (
          ((f = u ? yr(u) : window),
          (p = f.nodeName && f.nodeName.toLowerCase()),
          p === "select" || (p === "input" && f.type === "file"))
        )
          var N = iv;
        else if (Yc(f))
          if (sh) N = sv;
          else {
            N = lv;
            var x = ov;
          }
        else
          (p = f.nodeName) &&
            p.toLowerCase() === "input" &&
            (f.type === "checkbox" || f.type === "radio") &&
            (N = av);
        if (N && (N = N(e, u))) {
          ah(c, N, n, d);
          break e;
        }
        (x && x(e, f, u),
          e === "focusout" &&
            (x = f._wrapperState) &&
            x.controlled &&
            f.type === "number" &&
            ts(f, "number", f.value));
      }
      switch (((x = u ? yr(u) : window), e)) {
        case "focusin":
          (Yc(x) || x.contentEditable === "true") &&
            ((gr = x), (ps = u), (Ei = null));
          break;
        case "focusout":
          Ei = ps = gr = null;
          break;
        case "mousedown":
          hs = !0;
          break;
        case "contextmenu":
        case "mouseup":
        case "dragend":
          ((hs = !1), ed(c, n, d));
          break;
        case "selectionchange":
          if (dv) break;
        case "keydown":
        case "keyup":
          ed(c, n, d);
      }
      var O;
      if (xu)
        e: {
          switch (e) {
            case "compositionstart":
              var I = "onCompositionStart";
              break e;
            case "compositionend":
              I = "onCompositionEnd";
              break e;
            case "compositionupdate":
              I = "onCompositionUpdate";
              break e;
          }
          I = void 0;
        }
      else
        hr
          ? oh(e, n) && (I = "onCompositionEnd")
          : e === "keydown" && n.keyCode === 229 && (I = "onCompositionStart");
      (I &&
        (ih &&
          n.locale !== "ko" &&
          (hr || I !== "onCompositionStart"
            ? I === "onCompositionEnd" && hr && (O = rh())
            : ((hn = d),
              (vu = "value" in hn ? hn.value : hn.textContent),
              (hr = !0))),
        (x = ol(u, I)),
        0 < x.length &&
          ((I = new Gc(I, e, null, n, d)),
          c.push({ event: I, listeners: x }),
          O ? (I.data = O) : ((O = lh(n)), O !== null && (I.data = O)))),
        (O = Jb ? ev(e, n) : tv(e, n)) &&
          ((u = ol(u, "onBeforeInput")),
          0 < u.length &&
            ((d = new Gc("onBeforeInput", "beforeinput", null, n, d)),
            c.push({ event: d, listeners: u }),
            (d.data = O))));
    }
    bh(c, t);
  });
}
function zi(e, t, n) {
  return { instance: e, listener: t, currentTarget: n };
}
function ol(e, t) {
  for (var n = t + "Capture", r = []; e !== null;) {
    var i = e,
      o = i.stateNode;
    (i.tag === 5 &&
      o !== null &&
      ((i = o),
      (o = Ri(e, n)),
      o != null && r.unshift(zi(e, o, i)),
      (o = Ri(e, t)),
      o != null && r.push(zi(e, o, i))),
      (e = e.return));
  }
  return r;
}
function ar(e) {
  if (e === null) return null;
  do e = e.return;
  while (e && e.tag !== 5);
  return e || null;
}
function rd(e, t, n, r, i) {
  for (var o = t._reactName, l = []; n !== null && n !== r;) {
    var a = n,
      s = a.alternate,
      u = a.stateNode;
    if (s !== null && s === r) break;
    (a.tag === 5 &&
      u !== null &&
      ((a = u),
      i
        ? ((s = Ri(n, o)), s != null && l.unshift(zi(n, s, a)))
        : i || ((s = Ri(n, o)), s != null && l.push(zi(n, s, a)))),
      (n = n.return));
  }
  l.length !== 0 && e.push({ event: t, listeners: l });
}
var gv = /\r\n?/g,
  mv = /\u0000|\uFFFD/g;
function id(e) {
  return (typeof e == "string" ? e : "" + e)
    .replace(
      gv,
      `
`,
    )
    .replace(mv, "");
}
function vo(e, t, n) {
  if (((t = id(t)), id(e) !== t && n)) throw Error(P(425));
}
function ll() {}
var gs = null,
  ms = null;
function ys(e, t) {
  return (
    e === "textarea" ||
    e === "noscript" ||
    typeof t.children == "string" ||
    typeof t.children == "number" ||
    (typeof t.dangerouslySetInnerHTML == "object" &&
      t.dangerouslySetInnerHTML !== null &&
      t.dangerouslySetInnerHTML.__html != null)
  );
}
var bs = typeof setTimeout == "function" ? setTimeout : void 0,
  yv = typeof clearTimeout == "function" ? clearTimeout : void 0,
  od = typeof Promise == "function" ? Promise : void 0,
  bv =
    typeof queueMicrotask == "function"
      ? queueMicrotask
      : typeof od < "u"
        ? function (e) {
            return od.resolve(null).then(e).catch(vv);
          }
        : bs;
function vv(e) {
  setTimeout(function () {
    throw e;
  });
}
function ya(e, t) {
  var n = t,
    r = 0;
  do {
    var i = n.nextSibling;
    if ((e.removeChild(n), i && i.nodeType === 8))
      if (((n = i.data), n === "/$")) {
        if (r === 0) {
          (e.removeChild(i), Mi(t));
          return;
        }
        r--;
      } else (n !== "$" && n !== "$?" && n !== "$!") || r++;
    n = i;
  } while (n);
  Mi(t);
}
function wn(e) {
  for (; e != null; e = e.nextSibling) {
    var t = e.nodeType;
    if (t === 1 || t === 3) break;
    if (t === 8) {
      if (((t = e.data), t === "$" || t === "$!" || t === "$?")) break;
      if (t === "/$") return null;
    }
  }
  return e;
}
function ld(e) {
  e = e.previousSibling;
  for (var t = 0; e;) {
    if (e.nodeType === 8) {
      var n = e.data;
      if (n === "$" || n === "$!" || n === "$?") {
        if (t === 0) return e;
        t--;
      } else n === "/$" && t++;
    }
    e = e.previousSibling;
  }
  return null;
}
var jr = Math.random().toString(36).slice(2),
  Pt = "__reactFiber$" + jr,
  Fi = "__reactProps$" + jr,
  Zt = "__reactContainer$" + jr,
  vs = "__reactEvents$" + jr,
  Ev = "__reactListeners$" + jr,
  wv = "__reactHandles$" + jr;
function Fn(e) {
  var t = e[Pt];
  if (t) return t;
  for (var n = e.parentNode; n;) {
    if ((t = n[Zt] || n[Pt])) {
      if (
        ((n = t.alternate),
        t.child !== null || (n !== null && n.child !== null))
      )
        for (e = ld(e); e !== null;) {
          if ((n = e[Pt])) return n;
          e = ld(e);
        }
      return t;
    }
    ((e = n), (n = e.parentNode));
  }
  return null;
}
function eo(e) {
  return (
    (e = e[Pt] || e[Zt]),
    !e || (e.tag !== 5 && e.tag !== 6 && e.tag !== 13 && e.tag !== 3) ? null : e
  );
}
function yr(e) {
  if (e.tag === 5 || e.tag === 6) return e.stateNode;
  throw Error(P(33));
}
function Pl(e) {
  return e[Fi] || null;
}
var Es = [],
  br = -1;
function An(e) {
  return { current: e };
}
function me(e) {
  0 > br || ((e.current = Es[br]), (Es[br] = null), br--);
}
function fe(e, t) {
  (br++, (Es[br] = e.current), (e.current = t));
}
var Cn = {},
  Be = An(Cn),
  Je = An(!1),
  Kn = Cn;
function Mr(e, t) {
  var n = e.type.contextTypes;
  if (!n) return Cn;
  var r = e.stateNode;
  if (r && r.__reactInternalMemoizedUnmaskedChildContext === t)
    return r.__reactInternalMemoizedMaskedChildContext;
  var i = {},
    o;
  for (o in n) i[o] = t[o];
  return (
    r &&
      ((e = e.stateNode),
      (e.__reactInternalMemoizedUnmaskedChildContext = t),
      (e.__reactInternalMemoizedMaskedChildContext = i)),
    i
  );
}
function et(e) {
  return ((e = e.childContextTypes), e != null);
}
function al() {
  (me(Je), me(Be));
}
function ad(e, t, n) {
  if (Be.current !== Cn) throw Error(P(168));
  (fe(Be, t), fe(Je, n));
}
function Eh(e, t, n) {
  var r = e.stateNode;
  if (((t = t.childContextTypes), typeof r.getChildContext != "function"))
    return n;
  r = r.getChildContext();
  for (var i in r) if (!(i in t)) throw Error(P(108, ob(e) || "Unknown", i));
  return Ee({}, n, r);
}
function sl(e) {
  return (
    (e =
      ((e = e.stateNode) && e.__reactInternalMemoizedMergedChildContext) || Cn),
    (Kn = Be.current),
    fe(Be, e),
    fe(Je, Je.current),
    !0
  );
}
function sd(e, t, n) {
  var r = e.stateNode;
  if (!r) throw Error(P(169));
  (n
    ? ((e = Eh(e, t, Kn)),
      (r.__reactInternalMemoizedMergedChildContext = e),
      me(Je),
      me(Be),
      fe(Be, e))
    : me(Je),
    fe(Je, n));
}
var Gt = null,
  zl = !1,
  ba = !1;
function wh(e) {
  Gt === null ? (Gt = [e]) : Gt.push(e);
}
function xv(e) {
  ((zl = !0), wh(e));
}
function Rn() {
  if (!ba && Gt !== null) {
    ba = !0;
    var e = 0,
      t = ae;
    try {
      var n = Gt;
      for (ae = 1; e < n.length; e++) {
        var r = n[e];
        do r = r(!0);
        while (r !== null);
      }
      ((Gt = null), (zl = !1));
    } catch (i) {
      throw (Gt !== null && (Gt = Gt.slice(e + 1)), Kp(gu, Rn), i);
    } finally {
      ((ae = t), (ba = !1));
    }
  }
  return null;
}
var vr = [],
  Er = 0,
  ul = null,
  cl = 0,
  ft = [],
  pt = 0,
  Vn = null,
  Kt = 1,
  Vt = "";
function Ln(e, t) {
  ((vr[Er++] = cl), (vr[Er++] = ul), (ul = e), (cl = t));
}
function xh(e, t, n) {
  ((ft[pt++] = Kt), (ft[pt++] = Vt), (ft[pt++] = Vn), (Vn = e));
  var r = Kt;
  e = Vt;
  var i = 32 - St(r) - 1;
  ((r &= ~(1 << i)), (n += 1));
  var o = 32 - St(t) + i;
  if (30 < o) {
    var l = i - (i % 5);
    ((o = (r & ((1 << l) - 1)).toString(32)),
      (r >>= l),
      (i -= l),
      (Kt = (1 << (32 - St(t) + i)) | (n << i) | r),
      (Vt = o + e));
  } else ((Kt = (1 << o) | (n << i) | r), (Vt = e));
}
function ku(e) {
  e.return !== null && (Ln(e, 1), xh(e, 1, 0));
}
function Su(e) {
  for (; e === ul;)
    ((ul = vr[--Er]), (vr[Er] = null), (cl = vr[--Er]), (vr[Er] = null));
  for (; e === Vn;)
    ((Vn = ft[--pt]),
      (ft[pt] = null),
      (Vt = ft[--pt]),
      (ft[pt] = null),
      (Kt = ft[--pt]),
      (ft[pt] = null));
}
var at = null,
  lt = null,
  ye = !1,
  kt = null;
function _h(e, t) {
  var n = gt(5, null, null, 0);
  ((n.elementType = "DELETED"),
    (n.stateNode = t),
    (n.return = e),
    (t = e.deletions),
    t === null ? ((e.deletions = [n]), (e.flags |= 16)) : t.push(n));
}
function ud(e, t) {
  switch (e.tag) {
    case 5:
      var n = e.type;
      return (
        (t =
          t.nodeType !== 1 || n.toLowerCase() !== t.nodeName.toLowerCase()
            ? null
            : t),
        t !== null
          ? ((e.stateNode = t), (at = e), (lt = wn(t.firstChild)), !0)
          : !1
      );
    case 6:
      return (
        (t = e.pendingProps === "" || t.nodeType !== 3 ? null : t),
        t !== null ? ((e.stateNode = t), (at = e), (lt = null), !0) : !1
      );
    case 13:
      return (
        (t = t.nodeType !== 8 ? null : t),
        t !== null
          ? ((n = Vn !== null ? { id: Kt, overflow: Vt } : null),
            (e.memoizedState = {
              dehydrated: t,
              treeContext: n,
              retryLane: 1073741824,
            }),
            (n = gt(18, null, null, 0)),
            (n.stateNode = t),
            (n.return = e),
            (e.child = n),
            (at = e),
            (lt = null),
            !0)
          : !1
      );
    default:
      return !1;
  }
}
function ws(e) {
  return (e.mode & 1) !== 0 && (e.flags & 128) === 0;
}
function xs(e) {
  if (ye) {
    var t = lt;
    if (t) {
      var n = t;
      if (!ud(e, t)) {
        if (ws(e)) throw Error(P(418));
        t = wn(n.nextSibling);
        var r = at;
        t && ud(e, t)
          ? _h(r, n)
          : ((e.flags = (e.flags & -4097) | 2), (ye = !1), (at = e));
      }
    } else {
      if (ws(e)) throw Error(P(418));
      ((e.flags = (e.flags & -4097) | 2), (ye = !1), (at = e));
    }
  }
}
function cd(e) {
  for (e = e.return; e !== null && e.tag !== 5 && e.tag !== 3 && e.tag !== 13;)
    e = e.return;
  at = e;
}
function Eo(e) {
  if (e !== at) return !1;
  if (!ye) return (cd(e), (ye = !0), !1);
  var t;
  if (
    ((t = e.tag !== 3) &&
      !(t = e.tag !== 5) &&
      ((t = e.type),
      (t = t !== "head" && t !== "body" && !ys(e.type, e.memoizedProps))),
    t && (t = lt))
  ) {
    if (ws(e)) throw (kh(), Error(P(418)));
    for (; t;) (_h(e, t), (t = wn(t.nextSibling)));
  }
  if ((cd(e), e.tag === 13)) {
    if (((e = e.memoizedState), (e = e !== null ? e.dehydrated : null), !e))
      throw Error(P(317));
    e: {
      for (e = e.nextSibling, t = 0; e;) {
        if (e.nodeType === 8) {
          var n = e.data;
          if (n === "/$") {
            if (t === 0) {
              lt = wn(e.nextSibling);
              break e;
            }
            t--;
          } else (n !== "$" && n !== "$!" && n !== "$?") || t++;
        }
        e = e.nextSibling;
      }
      lt = null;
    }
  } else lt = at ? wn(e.stateNode.nextSibling) : null;
  return !0;
}
function kh() {
  for (var e = lt; e;) e = wn(e.nextSibling);
}
function Lr() {
  ((lt = at = null), (ye = !1));
}
function Nu(e) {
  kt === null ? (kt = [e]) : kt.push(e);
}
var _v = en.ReactCurrentBatchConfig;
function ii(e, t, n) {
  if (
    ((e = n.ref), e !== null && typeof e != "function" && typeof e != "object")
  ) {
    if (n._owner) {
      if (((n = n._owner), n)) {
        if (n.tag !== 1) throw Error(P(309));
        var r = n.stateNode;
      }
      if (!r) throw Error(P(147, e));
      var i = r,
        o = "" + e;
      return t !== null &&
        t.ref !== null &&
        typeof t.ref == "function" &&
        t.ref._stringRef === o
        ? t.ref
        : ((t = function (l) {
            var a = i.refs;
            l === null ? delete a[o] : (a[o] = l);
          }),
          (t._stringRef = o),
          t);
    }
    if (typeof e != "string") throw Error(P(284));
    if (!n._owner) throw Error(P(290, e));
  }
  return e;
}
function wo(e, t) {
  throw (
    (e = Object.prototype.toString.call(t)),
    Error(
      P(
        31,
        e === "[object Object]"
          ? "object with keys {" + Object.keys(t).join(", ") + "}"
          : e,
      ),
    )
  );
}
function dd(e) {
  var t = e._init;
  return t(e._payload);
}
function Sh(e) {
  function t(h, m) {
    if (e) {
      var b = h.deletions;
      b === null ? ((h.deletions = [m]), (h.flags |= 16)) : b.push(m);
    }
  }
  function n(h, m) {
    if (!e) return null;
    for (; m !== null;) (t(h, m), (m = m.sibling));
    return null;
  }
  function r(h, m) {
    for (h = new Map(); m !== null;)
      (m.key !== null ? h.set(m.key, m) : h.set(m.index, m), (m = m.sibling));
    return h;
  }
  function i(h, m) {
    return ((h = Sn(h, m)), (h.index = 0), (h.sibling = null), h);
  }
  function o(h, m, b) {
    return (
      (h.index = b),
      e
        ? ((b = h.alternate),
          b !== null
            ? ((b = b.index), b < m ? ((h.flags |= 2), m) : b)
            : ((h.flags |= 2), m))
        : ((h.flags |= 1048576), m)
    );
  }
  function l(h) {
    return (e && h.alternate === null && (h.flags |= 2), h);
  }
  function a(h, m, b, _) {
    return m === null || m.tag !== 6
      ? ((m = Sa(b, h.mode, _)), (m.return = h), m)
      : ((m = i(m, b)), (m.return = h), m);
  }
  function s(h, m, b, _) {
    var N = b.type;
    return N === pr
      ? d(h, m, b.props.children, _, b.key)
      : m !== null &&
          (m.elementType === N ||
            (typeof N == "object" &&
              N !== null &&
              N.$$typeof === cn &&
              dd(N) === m.type))
        ? ((_ = i(m, b.props)), (_.ref = ii(h, m, b)), (_.return = h), _)
        : ((_ = Vo(b.type, b.key, b.props, null, h.mode, _)),
          (_.ref = ii(h, m, b)),
          (_.return = h),
          _);
  }
  function u(h, m, b, _) {
    return m === null ||
      m.tag !== 4 ||
      m.stateNode.containerInfo !== b.containerInfo ||
      m.stateNode.implementation !== b.implementation
      ? ((m = Na(b, h.mode, _)), (m.return = h), m)
      : ((m = i(m, b.children || [])), (m.return = h), m);
  }
  function d(h, m, b, _, N) {
    return m === null || m.tag !== 7
      ? ((m = Hn(b, h.mode, _, N)), (m.return = h), m)
      : ((m = i(m, b)), (m.return = h), m);
  }
  function c(h, m, b) {
    if ((typeof m == "string" && m !== "") || typeof m == "number")
      return ((m = Sa("" + m, h.mode, b)), (m.return = h), m);
    if (typeof m == "object" && m !== null) {
      switch (m.$$typeof) {
        case uo:
          return (
            (b = Vo(m.type, m.key, m.props, null, h.mode, b)),
            (b.ref = ii(h, null, m)),
            (b.return = h),
            b
          );
        case fr:
          return ((m = Na(m, h.mode, b)), (m.return = h), m);
        case cn:
          var _ = m._init;
          return c(h, _(m._payload), b);
      }
      if (pi(m) || Jr(m))
        return ((m = Hn(m, h.mode, b, null)), (m.return = h), m);
      wo(h, m);
    }
    return null;
  }
  function f(h, m, b, _) {
    var N = m !== null ? m.key : null;
    if ((typeof b == "string" && b !== "") || typeof b == "number")
      return N !== null ? null : a(h, m, "" + b, _);
    if (typeof b == "object" && b !== null) {
      switch (b.$$typeof) {
        case uo:
          return b.key === N ? s(h, m, b, _) : null;
        case fr:
          return b.key === N ? u(h, m, b, _) : null;
        case cn:
          return ((N = b._init), f(h, m, N(b._payload), _));
      }
      if (pi(b) || Jr(b)) return N !== null ? null : d(h, m, b, _, null);
      wo(h, b);
    }
    return null;
  }
  function p(h, m, b, _, N) {
    if ((typeof _ == "string" && _ !== "") || typeof _ == "number")
      return ((h = h.get(b) || null), a(m, h, "" + _, N));
    if (typeof _ == "object" && _ !== null) {
      switch (_.$$typeof) {
        case uo:
          return (
            (h = h.get(_.key === null ? b : _.key) || null),
            s(m, h, _, N)
          );
        case fr:
          return (
            (h = h.get(_.key === null ? b : _.key) || null),
            u(m, h, _, N)
          );
        case cn:
          var x = _._init;
          return p(h, m, b, x(_._payload), N);
      }
      if (pi(_) || Jr(_)) return ((h = h.get(b) || null), d(m, h, _, N, null));
      wo(m, _);
    }
    return null;
  }
  function g(h, m, b, _) {
    for (
      var N = null, x = null, O = m, I = (m = 0), U = null;
      O !== null && I < b.length;
      I++
    ) {
      O.index > I ? ((U = O), (O = null)) : (U = O.sibling);
      var S = f(h, O, b[I], _);
      if (S === null) {
        O === null && (O = U);
        break;
      }
      (e && O && S.alternate === null && t(h, O),
        (m = o(S, m, I)),
        x === null ? (N = S) : (x.sibling = S),
        (x = S),
        (O = U));
    }
    if (I === b.length) return (n(h, O), ye && Ln(h, I), N);
    if (O === null) {
      for (; I < b.length; I++)
        ((O = c(h, b[I], _)),
          O !== null &&
            ((m = o(O, m, I)),
            x === null ? (N = O) : (x.sibling = O),
            (x = O)));
      return (ye && Ln(h, I), N);
    }
    for (O = r(h, O); I < b.length; I++)
      ((U = p(O, h, I, b[I], _)),
        U !== null &&
          (e && U.alternate !== null && O.delete(U.key === null ? I : U.key),
          (m = o(U, m, I)),
          x === null ? (N = U) : (x.sibling = U),
          (x = U)));
    return (
      e &&
        O.forEach(function (F) {
          return t(h, F);
        }),
      ye && Ln(h, I),
      N
    );
  }
  function y(h, m, b, _) {
    var N = Jr(b);
    if (typeof N != "function") throw Error(P(150));
    if (((b = N.call(b)), b == null)) throw Error(P(151));
    for (
      var x = (N = null), O = m, I = (m = 0), U = null, S = b.next();
      O !== null && !S.done;
      I++, S = b.next()
    ) {
      O.index > I ? ((U = O), (O = null)) : (U = O.sibling);
      var F = f(h, O, S.value, _);
      if (F === null) {
        O === null && (O = U);
        break;
      }
      (e && O && F.alternate === null && t(h, O),
        (m = o(F, m, I)),
        x === null ? (N = F) : (x.sibling = F),
        (x = F),
        (O = U));
    }
    if (S.done) return (n(h, O), ye && Ln(h, I), N);
    if (O === null) {
      for (; !S.done; I++, S = b.next())
        ((S = c(h, S.value, _)),
          S !== null &&
            ((m = o(S, m, I)),
            x === null ? (N = S) : (x.sibling = S),
            (x = S)));
      return (ye && Ln(h, I), N);
    }
    for (O = r(h, O); !S.done; I++, S = b.next())
      ((S = p(O, h, I, S.value, _)),
        S !== null &&
          (e && S.alternate !== null && O.delete(S.key === null ? I : S.key),
          (m = o(S, m, I)),
          x === null ? (N = S) : (x.sibling = S),
          (x = S)));
    return (
      e &&
        O.forEach(function (L) {
          return t(h, L);
        }),
      ye && Ln(h, I),
      N
    );
  }
  function E(h, m, b, _) {
    if (
      (typeof b == "object" &&
        b !== null &&
        b.type === pr &&
        b.key === null &&
        (b = b.props.children),
      typeof b == "object" && b !== null)
    ) {
      switch (b.$$typeof) {
        case uo:
          e: {
            for (var N = b.key, x = m; x !== null;) {
              if (x.key === N) {
                if (((N = b.type), N === pr)) {
                  if (x.tag === 7) {
                    (n(h, x.sibling),
                      (m = i(x, b.props.children)),
                      (m.return = h),
                      (h = m));
                    break e;
                  }
                } else if (
                  x.elementType === N ||
                  (typeof N == "object" &&
                    N !== null &&
                    N.$$typeof === cn &&
                    dd(N) === x.type)
                ) {
                  (n(h, x.sibling),
                    (m = i(x, b.props)),
                    (m.ref = ii(h, x, b)),
                    (m.return = h),
                    (h = m));
                  break e;
                }
                n(h, x);
                break;
              } else t(h, x);
              x = x.sibling;
            }
            b.type === pr
              ? ((m = Hn(b.props.children, h.mode, _, b.key)),
                (m.return = h),
                (h = m))
              : ((_ = Vo(b.type, b.key, b.props, null, h.mode, _)),
                (_.ref = ii(h, m, b)),
                (_.return = h),
                (h = _));
          }
          return l(h);
        case fr:
          e: {
            for (x = b.key; m !== null;) {
              if (m.key === x)
                if (
                  m.tag === 4 &&
                  m.stateNode.containerInfo === b.containerInfo &&
                  m.stateNode.implementation === b.implementation
                ) {
                  (n(h, m.sibling),
                    (m = i(m, b.children || [])),
                    (m.return = h),
                    (h = m));
                  break e;
                } else {
                  n(h, m);
                  break;
                }
              else t(h, m);
              m = m.sibling;
            }
            ((m = Na(b, h.mode, _)), (m.return = h), (h = m));
          }
          return l(h);
        case cn:
          return ((x = b._init), E(h, m, x(b._payload), _));
      }
      if (pi(b)) return g(h, m, b, _);
      if (Jr(b)) return y(h, m, b, _);
      wo(h, b);
    }
    return (typeof b == "string" && b !== "") || typeof b == "number"
      ? ((b = "" + b),
        m !== null && m.tag === 6
          ? (n(h, m.sibling), (m = i(m, b)), (m.return = h), (h = m))
          : (n(h, m), (m = Sa(b, h.mode, _)), (m.return = h), (h = m)),
        l(h))
      : n(h, m);
  }
  return E;
}
var Dr = Sh(!0),
  Nh = Sh(!1),
  dl = An(null),
  fl = null,
  wr = null,
  Cu = null;
function Tu() {
  Cu = wr = fl = null;
}
function Au(e) {
  var t = dl.current;
  (me(dl), (e._currentValue = t));
}
function _s(e, t, n) {
  for (; e !== null;) {
    var r = e.alternate;
    if (
      ((e.childLanes & t) !== t
        ? ((e.childLanes |= t), r !== null && (r.childLanes |= t))
        : r !== null && (r.childLanes & t) !== t && (r.childLanes |= t),
      e === n)
    )
      break;
    e = e.return;
  }
}
function Tr(e, t) {
  ((fl = e),
    (Cu = wr = null),
    (e = e.dependencies),
    e !== null &&
      e.firstContext !== null &&
      (e.lanes & t && (Xe = !0), (e.firstContext = null)));
}
function yt(e) {
  var t = e._currentValue;
  if (Cu !== e)
    if (((e = { context: e, memoizedValue: t, next: null }), wr === null)) {
      if (fl === null) throw Error(P(308));
      ((wr = e), (fl.dependencies = { lanes: 0, firstContext: e }));
    } else wr = wr.next = e;
  return t;
}
var Bn = null;
function Ru(e) {
  Bn === null ? (Bn = [e]) : Bn.push(e);
}
function Ch(e, t, n, r) {
  var i = t.interleaved;
  return (
    i === null ? ((n.next = n), Ru(t)) : ((n.next = i.next), (i.next = n)),
    (t.interleaved = n),
    Xt(e, r)
  );
}
function Xt(e, t) {
  e.lanes |= t;
  var n = e.alternate;
  for (n !== null && (n.lanes |= t), n = e, e = e.return; e !== null;)
    ((e.childLanes |= t),
      (n = e.alternate),
      n !== null && (n.childLanes |= t),
      (n = e),
      (e = e.return));
  return n.tag === 3 ? n.stateNode : null;
}
var dn = !1;
function Ou(e) {
  e.updateQueue = {
    baseState: e.memoizedState,
    firstBaseUpdate: null,
    lastBaseUpdate: null,
    shared: { pending: null, interleaved: null, lanes: 0 },
    effects: null,
  };
}
function Th(e, t) {
  ((e = e.updateQueue),
    t.updateQueue === e &&
      (t.updateQueue = {
        baseState: e.baseState,
        firstBaseUpdate: e.firstBaseUpdate,
        lastBaseUpdate: e.lastBaseUpdate,
        shared: e.shared,
        effects: e.effects,
      }));
}
function qt(e, t) {
  return {
    eventTime: e,
    lane: t,
    tag: 0,
    payload: null,
    callback: null,
    next: null,
  };
}
function xn(e, t, n) {
  var r = e.updateQueue;
  if (r === null) return null;
  if (((r = r.shared), ie & 2)) {
    var i = r.pending;
    return (
      i === null ? (t.next = t) : ((t.next = i.next), (i.next = t)),
      (r.pending = t),
      Xt(e, n)
    );
  }
  return (
    (i = r.interleaved),
    i === null ? ((t.next = t), Ru(r)) : ((t.next = i.next), (i.next = t)),
    (r.interleaved = t),
    Xt(e, n)
  );
}
function $o(e, t, n) {
  if (
    ((t = t.updateQueue), t !== null && ((t = t.shared), (n & 4194240) !== 0))
  ) {
    var r = t.lanes;
    ((r &= e.pendingLanes), (n |= r), (t.lanes = n), mu(e, n));
  }
}
function fd(e, t) {
  var n = e.updateQueue,
    r = e.alternate;
  if (r !== null && ((r = r.updateQueue), n === r)) {
    var i = null,
      o = null;
    if (((n = n.firstBaseUpdate), n !== null)) {
      do {
        var l = {
          eventTime: n.eventTime,
          lane: n.lane,
          tag: n.tag,
          payload: n.payload,
          callback: n.callback,
          next: null,
        };
        (o === null ? (i = o = l) : (o = o.next = l), (n = n.next));
      } while (n !== null);
      o === null ? (i = o = t) : (o = o.next = t);
    } else i = o = t;
    ((n = {
      baseState: r.baseState,
      firstBaseUpdate: i,
      lastBaseUpdate: o,
      shared: r.shared,
      effects: r.effects,
    }),
      (e.updateQueue = n));
    return;
  }
  ((e = n.lastBaseUpdate),
    e === null ? (n.firstBaseUpdate = t) : (e.next = t),
    (n.lastBaseUpdate = t));
}
function pl(e, t, n, r) {
  var i = e.updateQueue;
  dn = !1;
  var o = i.firstBaseUpdate,
    l = i.lastBaseUpdate,
    a = i.shared.pending;
  if (a !== null) {
    i.shared.pending = null;
    var s = a,
      u = s.next;
    ((s.next = null), l === null ? (o = u) : (l.next = u), (l = s));
    var d = e.alternate;
    d !== null &&
      ((d = d.updateQueue),
      (a = d.lastBaseUpdate),
      a !== l &&
        (a === null ? (d.firstBaseUpdate = u) : (a.next = u),
        (d.lastBaseUpdate = s)));
  }
  if (o !== null) {
    var c = i.baseState;
    ((l = 0), (d = u = s = null), (a = o));
    do {
      var f = a.lane,
        p = a.eventTime;
      if ((r & f) === f) {
        d !== null &&
          (d = d.next =
            {
              eventTime: p,
              lane: 0,
              tag: a.tag,
              payload: a.payload,
              callback: a.callback,
              next: null,
            });
        e: {
          var g = e,
            y = a;
          switch (((f = t), (p = n), y.tag)) {
            case 1:
              if (((g = y.payload), typeof g == "function")) {
                c = g.call(p, c, f);
                break e;
              }
              c = g;
              break e;
            case 3:
              g.flags = (g.flags & -65537) | 128;
            case 0:
              if (
                ((g = y.payload),
                (f = typeof g == "function" ? g.call(p, c, f) : g),
                f == null)
              )
                break e;
              c = Ee({}, c, f);
              break e;
            case 2:
              dn = !0;
          }
        }
        a.callback !== null &&
          a.lane !== 0 &&
          ((e.flags |= 64),
          (f = i.effects),
          f === null ? (i.effects = [a]) : f.push(a));
      } else
        ((p = {
          eventTime: p,
          lane: f,
          tag: a.tag,
          payload: a.payload,
          callback: a.callback,
          next: null,
        }),
          d === null ? ((u = d = p), (s = c)) : (d = d.next = p),
          (l |= f));
      if (((a = a.next), a === null)) {
        if (((a = i.shared.pending), a === null)) break;
        ((f = a),
          (a = f.next),
          (f.next = null),
          (i.lastBaseUpdate = f),
          (i.shared.pending = null));
      }
    } while (!0);
    if (
      (d === null && (s = c),
      (i.baseState = s),
      (i.firstBaseUpdate = u),
      (i.lastBaseUpdate = d),
      (t = i.shared.interleaved),
      t !== null)
    ) {
      i = t;
      do ((l |= i.lane), (i = i.next));
      while (i !== t);
    } else o === null && (i.shared.lanes = 0);
    ((Yn |= l), (e.lanes = l), (e.memoizedState = c));
  }
}
function pd(e, t, n) {
  if (((e = t.effects), (t.effects = null), e !== null))
    for (t = 0; t < e.length; t++) {
      var r = e[t],
        i = r.callback;
      if (i !== null) {
        if (((r.callback = null), (r = n), typeof i != "function"))
          throw Error(P(191, i));
        i.call(r);
      }
    }
}
var to = {},
  Ft = An(to),
  Bi = An(to),
  Ui = An(to);
function Un(e) {
  if (e === to) throw Error(P(174));
  return e;
}
function Iu(e, t) {
  switch ((fe(Ui, t), fe(Bi, e), fe(Ft, to), (e = t.nodeType), e)) {
    case 9:
    case 11:
      t = (t = t.documentElement) ? t.namespaceURI : rs(null, "");
      break;
    default:
      ((e = e === 8 ? t.parentNode : t),
        (t = e.namespaceURI || null),
        (e = e.tagName),
        (t = rs(t, e)));
  }
  (me(Ft), fe(Ft, t));
}
function Pr() {
  (me(Ft), me(Bi), me(Ui));
}
function Ah(e) {
  Un(Ui.current);
  var t = Un(Ft.current),
    n = rs(t, e.type);
  t !== n && (fe(Bi, e), fe(Ft, n));
}
function Mu(e) {
  Bi.current === e && (me(Ft), me(Bi));
}
var be = An(0);
function hl(e) {
  for (var t = e; t !== null;) {
    if (t.tag === 13) {
      var n = t.memoizedState;
      if (
        n !== null &&
        ((n = n.dehydrated), n === null || n.data === "$?" || n.data === "$!")
      )
        return t;
    } else if (t.tag === 19 && t.memoizedProps.revealOrder !== void 0) {
      if (t.flags & 128) return t;
    } else if (t.child !== null) {
      ((t.child.return = t), (t = t.child));
      continue;
    }
    if (t === e) break;
    for (; t.sibling === null;) {
      if (t.return === null || t.return === e) return null;
      t = t.return;
    }
    ((t.sibling.return = t.return), (t = t.sibling));
  }
  return null;
}
var va = [];
function Lu() {
  for (var e = 0; e < va.length; e++)
    va[e]._workInProgressVersionPrimary = null;
  va.length = 0;
}
var Ho = en.ReactCurrentDispatcher,
  Ea = en.ReactCurrentBatchConfig,
  qn = 0,
  ve = null,
  Te = null,
  Re = null,
  gl = !1,
  wi = !1,
  $i = 0,
  kv = 0;
function De() {
  throw Error(P(321));
}
function Du(e, t) {
  if (t === null) return !1;
  for (var n = 0; n < t.length && n < e.length; n++)
    if (!Tt(e[n], t[n])) return !1;
  return !0;
}
function Pu(e, t, n, r, i, o) {
  if (
    ((qn = o),
    (ve = t),
    (t.memoizedState = null),
    (t.updateQueue = null),
    (t.lanes = 0),
    (Ho.current = e === null || e.memoizedState === null ? Tv : Av),
    (e = n(r, i)),
    wi)
  ) {
    o = 0;
    do {
      if (((wi = !1), ($i = 0), 25 <= o)) throw Error(P(301));
      ((o += 1),
        (Re = Te = null),
        (t.updateQueue = null),
        (Ho.current = Rv),
        (e = n(r, i)));
    } while (wi);
  }
  if (
    ((Ho.current = ml),
    (t = Te !== null && Te.next !== null),
    (qn = 0),
    (Re = Te = ve = null),
    (gl = !1),
    t)
  )
    throw Error(P(300));
  return e;
}
function zu() {
  var e = $i !== 0;
  return (($i = 0), e);
}
function Lt() {
  var e = {
    memoizedState: null,
    baseState: null,
    baseQueue: null,
    queue: null,
    next: null,
  };
  return (Re === null ? (ve.memoizedState = Re = e) : (Re = Re.next = e), Re);
}
function bt() {
  if (Te === null) {
    var e = ve.alternate;
    e = e !== null ? e.memoizedState : null;
  } else e = Te.next;
  var t = Re === null ? ve.memoizedState : Re.next;
  if (t !== null) ((Re = t), (Te = e));
  else {
    if (e === null) throw Error(P(310));
    ((Te = e),
      (e = {
        memoizedState: Te.memoizedState,
        baseState: Te.baseState,
        baseQueue: Te.baseQueue,
        queue: Te.queue,
        next: null,
      }),
      Re === null ? (ve.memoizedState = Re = e) : (Re = Re.next = e));
  }
  return Re;
}
function Hi(e, t) {
  return typeof t == "function" ? t(e) : t;
}
function wa(e) {
  var t = bt(),
    n = t.queue;
  if (n === null) throw Error(P(311));
  n.lastRenderedReducer = e;
  var r = Te,
    i = r.baseQueue,
    o = n.pending;
  if (o !== null) {
    if (i !== null) {
      var l = i.next;
      ((i.next = o.next), (o.next = l));
    }
    ((r.baseQueue = i = o), (n.pending = null));
  }
  if (i !== null) {
    ((o = i.next), (r = r.baseState));
    var a = (l = null),
      s = null,
      u = o;
    do {
      var d = u.lane;
      if ((qn & d) === d)
        (s !== null &&
          (s = s.next =
            {
              lane: 0,
              action: u.action,
              hasEagerState: u.hasEagerState,
              eagerState: u.eagerState,
              next: null,
            }),
          (r = u.hasEagerState ? u.eagerState : e(r, u.action)));
      else {
        var c = {
          lane: d,
          action: u.action,
          hasEagerState: u.hasEagerState,
          eagerState: u.eagerState,
          next: null,
        };
        (s === null ? ((a = s = c), (l = r)) : (s = s.next = c),
          (ve.lanes |= d),
          (Yn |= d));
      }
      u = u.next;
    } while (u !== null && u !== o);
    (s === null ? (l = r) : (s.next = a),
      Tt(r, t.memoizedState) || (Xe = !0),
      (t.memoizedState = r),
      (t.baseState = l),
      (t.baseQueue = s),
      (n.lastRenderedState = r));
  }
  if (((e = n.interleaved), e !== null)) {
    i = e;
    do ((o = i.lane), (ve.lanes |= o), (Yn |= o), (i = i.next));
    while (i !== e);
  } else i === null && (n.lanes = 0);
  return [t.memoizedState, n.dispatch];
}
function xa(e) {
  var t = bt(),
    n = t.queue;
  if (n === null) throw Error(P(311));
  n.lastRenderedReducer = e;
  var r = n.dispatch,
    i = n.pending,
    o = t.memoizedState;
  if (i !== null) {
    n.pending = null;
    var l = (i = i.next);
    do ((o = e(o, l.action)), (l = l.next));
    while (l !== i);
    (Tt(o, t.memoizedState) || (Xe = !0),
      (t.memoizedState = o),
      t.baseQueue === null && (t.baseState = o),
      (n.lastRenderedState = o));
  }
  return [o, r];
}
function Rh() {}
function Oh(e, t) {
  var n = ve,
    r = bt(),
    i = t(),
    o = !Tt(r.memoizedState, i);
  if (
    (o && ((r.memoizedState = i), (Xe = !0)),
    (r = r.queue),
    Fu(Lh.bind(null, n, r, e), [e]),
    r.getSnapshot !== t || o || (Re !== null && Re.memoizedState.tag & 1))
  ) {
    if (
      ((n.flags |= 2048),
      ji(9, Mh.bind(null, n, r, i, t), void 0, null),
      Oe === null)
    )
      throw Error(P(349));
    qn & 30 || Ih(n, t, i);
  }
  return i;
}
function Ih(e, t, n) {
  ((e.flags |= 16384),
    (e = { getSnapshot: t, value: n }),
    (t = ve.updateQueue),
    t === null
      ? ((t = { lastEffect: null, stores: null }),
        (ve.updateQueue = t),
        (t.stores = [e]))
      : ((n = t.stores), n === null ? (t.stores = [e]) : n.push(e)));
}
function Mh(e, t, n, r) {
  ((t.value = n), (t.getSnapshot = r), Dh(t) && Ph(e));
}
function Lh(e, t, n) {
  return n(function () {
    Dh(t) && Ph(e);
  });
}
function Dh(e) {
  var t = e.getSnapshot;
  e = e.value;
  try {
    var n = t();
    return !Tt(e, n);
  } catch {
    return !0;
  }
}
function Ph(e) {
  var t = Xt(e, 1);
  t !== null && Nt(t, e, 1, -1);
}
function hd(e) {
  var t = Lt();
  return (
    typeof e == "function" && (e = e()),
    (t.memoizedState = t.baseState = e),
    (e = {
      pending: null,
      interleaved: null,
      lanes: 0,
      dispatch: null,
      lastRenderedReducer: Hi,
      lastRenderedState: e,
    }),
    (t.queue = e),
    (e = e.dispatch = Cv.bind(null, ve, e)),
    [t.memoizedState, e]
  );
}
function ji(e, t, n, r) {
  return (
    (e = { tag: e, create: t, destroy: n, deps: r, next: null }),
    (t = ve.updateQueue),
    t === null
      ? ((t = { lastEffect: null, stores: null }),
        (ve.updateQueue = t),
        (t.lastEffect = e.next = e))
      : ((n = t.lastEffect),
        n === null
          ? (t.lastEffect = e.next = e)
          : ((r = n.next), (n.next = e), (e.next = r), (t.lastEffect = e))),
    e
  );
}
function zh() {
  return bt().memoizedState;
}
function jo(e, t, n, r) {
  var i = Lt();
  ((ve.flags |= e),
    (i.memoizedState = ji(1 | t, n, void 0, r === void 0 ? null : r)));
}
function Fl(e, t, n, r) {
  var i = bt();
  r = r === void 0 ? null : r;
  var o = void 0;
  if (Te !== null) {
    var l = Te.memoizedState;
    if (((o = l.destroy), r !== null && Du(r, l.deps))) {
      i.memoizedState = ji(t, n, o, r);
      return;
    }
  }
  ((ve.flags |= e), (i.memoizedState = ji(1 | t, n, o, r)));
}
function gd(e, t) {
  return jo(8390656, 8, e, t);
}
function Fu(e, t) {
  return Fl(2048, 8, e, t);
}
function Fh(e, t) {
  return Fl(4, 2, e, t);
}
function Bh(e, t) {
  return Fl(4, 4, e, t);
}
function Uh(e, t) {
  if (typeof t == "function")
    return (
      (e = e()),
      t(e),
      function () {
        t(null);
      }
    );
  if (t != null)
    return (
      (e = e()),
      (t.current = e),
      function () {
        t.current = null;
      }
    );
}
function $h(e, t, n) {
  return (
    (n = n != null ? n.concat([e]) : null),
    Fl(4, 4, Uh.bind(null, t, e), n)
  );
}
function Bu() {}
function Hh(e, t) {
  var n = bt();
  t = t === void 0 ? null : t;
  var r = n.memoizedState;
  return r !== null && t !== null && Du(t, r[1])
    ? r[0]
    : ((n.memoizedState = [e, t]), e);
}
function jh(e, t) {
  var n = bt();
  t = t === void 0 ? null : t;
  var r = n.memoizedState;
  return r !== null && t !== null && Du(t, r[1])
    ? r[0]
    : ((e = e()), (n.memoizedState = [e, t]), e);
}
function Wh(e, t, n) {
  return qn & 21
    ? (Tt(n, t) || ((n = Yp()), (ve.lanes |= n), (Yn |= n), (e.baseState = !0)),
      t)
    : (e.baseState && ((e.baseState = !1), (Xe = !0)), (e.memoizedState = n));
}
function Sv(e, t) {
  var n = ae;
  ((ae = n !== 0 && 4 > n ? n : 4), e(!0));
  var r = Ea.transition;
  Ea.transition = {};
  try {
    (e(!1), t());
  } finally {
    ((ae = n), (Ea.transition = r));
  }
}
function Gh() {
  return bt().memoizedState;
}
function Nv(e, t, n) {
  var r = kn(e);
  if (
    ((n = {
      lane: r,
      action: n,
      hasEagerState: !1,
      eagerState: null,
      next: null,
    }),
    Kh(e))
  )
    Vh(t, n);
  else if (((n = Ch(e, t, n, r)), n !== null)) {
    var i = Ke();
    (Nt(n, e, r, i), qh(n, t, r));
  }
}
function Cv(e, t, n) {
  var r = kn(e),
    i = { lane: r, action: n, hasEagerState: !1, eagerState: null, next: null };
  if (Kh(e)) Vh(t, i);
  else {
    var o = e.alternate;
    if (
      e.lanes === 0 &&
      (o === null || o.lanes === 0) &&
      ((o = t.lastRenderedReducer), o !== null)
    )
      try {
        var l = t.lastRenderedState,
          a = o(l, n);
        if (((i.hasEagerState = !0), (i.eagerState = a), Tt(a, l))) {
          var s = t.interleaved;
          (s === null
            ? ((i.next = i), Ru(t))
            : ((i.next = s.next), (s.next = i)),
            (t.interleaved = i));
          return;
        }
      } catch {
      } finally {
      }
    ((n = Ch(e, t, i, r)),
      n !== null && ((i = Ke()), Nt(n, e, r, i), qh(n, t, r)));
  }
}
function Kh(e) {
  var t = e.alternate;
  return e === ve || (t !== null && t === ve);
}
function Vh(e, t) {
  wi = gl = !0;
  var n = e.pending;
  (n === null ? (t.next = t) : ((t.next = n.next), (n.next = t)),
    (e.pending = t));
}
function qh(e, t, n) {
  if (n & 4194240) {
    var r = t.lanes;
    ((r &= e.pendingLanes), (n |= r), (t.lanes = n), mu(e, n));
  }
}
var ml = {
    readContext: yt,
    useCallback: De,
    useContext: De,
    useEffect: De,
    useImperativeHandle: De,
    useInsertionEffect: De,
    useLayoutEffect: De,
    useMemo: De,
    useReducer: De,
    useRef: De,
    useState: De,
    useDebugValue: De,
    useDeferredValue: De,
    useTransition: De,
    useMutableSource: De,
    useSyncExternalStore: De,
    useId: De,
    unstable_isNewReconciler: !1,
  },
  Tv = {
    readContext: yt,
    useCallback: function (e, t) {
      return ((Lt().memoizedState = [e, t === void 0 ? null : t]), e);
    },
    useContext: yt,
    useEffect: gd,
    useImperativeHandle: function (e, t, n) {
      return (
        (n = n != null ? n.concat([e]) : null),
        jo(4194308, 4, Uh.bind(null, t, e), n)
      );
    },
    useLayoutEffect: function (e, t) {
      return jo(4194308, 4, e, t);
    },
    useInsertionEffect: function (e, t) {
      return jo(4, 2, e, t);
    },
    useMemo: function (e, t) {
      var n = Lt();
      return (
        (t = t === void 0 ? null : t),
        (e = e()),
        (n.memoizedState = [e, t]),
        e
      );
    },
    useReducer: function (e, t, n) {
      var r = Lt();
      return (
        (t = n !== void 0 ? n(t) : t),
        (r.memoizedState = r.baseState = t),
        (e = {
          pending: null,
          interleaved: null,
          lanes: 0,
          dispatch: null,
          lastRenderedReducer: e,
          lastRenderedState: t,
        }),
        (r.queue = e),
        (e = e.dispatch = Nv.bind(null, ve, e)),
        [r.memoizedState, e]
      );
    },
    useRef: function (e) {
      var t = Lt();
      return ((e = { current: e }), (t.memoizedState = e));
    },
    useState: hd,
    useDebugValue: Bu,
    useDeferredValue: function (e) {
      return (Lt().memoizedState = e);
    },
    useTransition: function () {
      var e = hd(!1),
        t = e[0];
      return ((e = Sv.bind(null, e[1])), (Lt().memoizedState = e), [t, e]);
    },
    useMutableSource: function () {},
    useSyncExternalStore: function (e, t, n) {
      var r = ve,
        i = Lt();
      if (ye) {
        if (n === void 0) throw Error(P(407));
        n = n();
      } else {
        if (((n = t()), Oe === null)) throw Error(P(349));
        qn & 30 || Ih(r, t, n);
      }
      i.memoizedState = n;
      var o = { value: n, getSnapshot: t };
      return (
        (i.queue = o),
        gd(Lh.bind(null, r, o, e), [e]),
        (r.flags |= 2048),
        ji(9, Mh.bind(null, r, o, n, t), void 0, null),
        n
      );
    },
    useId: function () {
      var e = Lt(),
        t = Oe.identifierPrefix;
      if (ye) {
        var n = Vt,
          r = Kt;
        ((n = (r & ~(1 << (32 - St(r) - 1))).toString(32) + n),
          (t = ":" + t + "R" + n),
          (n = $i++),
          0 < n && (t += "H" + n.toString(32)),
          (t += ":"));
      } else ((n = kv++), (t = ":" + t + "r" + n.toString(32) + ":"));
      return (e.memoizedState = t);
    },
    unstable_isNewReconciler: !1,
  },
  Av = {
    readContext: yt,
    useCallback: Hh,
    useContext: yt,
    useEffect: Fu,
    useImperativeHandle: $h,
    useInsertionEffect: Fh,
    useLayoutEffect: Bh,
    useMemo: jh,
    useReducer: wa,
    useRef: zh,
    useState: function () {
      return wa(Hi);
    },
    useDebugValue: Bu,
    useDeferredValue: function (e) {
      var t = bt();
      return Wh(t, Te.memoizedState, e);
    },
    useTransition: function () {
      var e = wa(Hi)[0],
        t = bt().memoizedState;
      return [e, t];
    },
    useMutableSource: Rh,
    useSyncExternalStore: Oh,
    useId: Gh,
    unstable_isNewReconciler: !1,
  },
  Rv = {
    readContext: yt,
    useCallback: Hh,
    useContext: yt,
    useEffect: Fu,
    useImperativeHandle: $h,
    useInsertionEffect: Fh,
    useLayoutEffect: Bh,
    useMemo: jh,
    useReducer: xa,
    useRef: zh,
    useState: function () {
      return xa(Hi);
    },
    useDebugValue: Bu,
    useDeferredValue: function (e) {
      var t = bt();
      return Te === null ? (t.memoizedState = e) : Wh(t, Te.memoizedState, e);
    },
    useTransition: function () {
      var e = xa(Hi)[0],
        t = bt().memoizedState;
      return [e, t];
    },
    useMutableSource: Rh,
    useSyncExternalStore: Oh,
    useId: Gh,
    unstable_isNewReconciler: !1,
  };
function xt(e, t) {
  if (e && e.defaultProps) {
    ((t = Ee({}, t)), (e = e.defaultProps));
    for (var n in e) t[n] === void 0 && (t[n] = e[n]);
    return t;
  }
  return t;
}
function ks(e, t, n, r) {
  ((t = e.memoizedState),
    (n = n(r, t)),
    (n = n == null ? t : Ee({}, t, n)),
    (e.memoizedState = n),
    e.lanes === 0 && (e.updateQueue.baseState = n));
}
var Bl = {
  isMounted: function (e) {
    return (e = e._reactInternals) ? Jn(e) === e : !1;
  },
  enqueueSetState: function (e, t, n) {
    e = e._reactInternals;
    var r = Ke(),
      i = kn(e),
      o = qt(r, i);
    ((o.payload = t),
      n != null && (o.callback = n),
      (t = xn(e, o, i)),
      t !== null && (Nt(t, e, i, r), $o(t, e, i)));
  },
  enqueueReplaceState: function (e, t, n) {
    e = e._reactInternals;
    var r = Ke(),
      i = kn(e),
      o = qt(r, i);
    ((o.tag = 1),
      (o.payload = t),
      n != null && (o.callback = n),
      (t = xn(e, o, i)),
      t !== null && (Nt(t, e, i, r), $o(t, e, i)));
  },
  enqueueForceUpdate: function (e, t) {
    e = e._reactInternals;
    var n = Ke(),
      r = kn(e),
      i = qt(n, r);
    ((i.tag = 2),
      t != null && (i.callback = t),
      (t = xn(e, i, r)),
      t !== null && (Nt(t, e, r, n), $o(t, e, r)));
  },
};
function md(e, t, n, r, i, o, l) {
  return (
    (e = e.stateNode),
    typeof e.shouldComponentUpdate == "function"
      ? e.shouldComponentUpdate(r, o, l)
      : t.prototype && t.prototype.isPureReactComponent
        ? !Di(n, r) || !Di(i, o)
        : !0
  );
}
function Yh(e, t, n) {
  var r = !1,
    i = Cn,
    o = t.contextType;
  return (
    typeof o == "object" && o !== null
      ? (o = yt(o))
      : ((i = et(t) ? Kn : Be.current),
        (r = t.contextTypes),
        (o = (r = r != null) ? Mr(e, i) : Cn)),
    (t = new t(n, o)),
    (e.memoizedState = t.state !== null && t.state !== void 0 ? t.state : null),
    (t.updater = Bl),
    (e.stateNode = t),
    (t._reactInternals = e),
    r &&
      ((e = e.stateNode),
      (e.__reactInternalMemoizedUnmaskedChildContext = i),
      (e.__reactInternalMemoizedMaskedChildContext = o)),
    t
  );
}
function yd(e, t, n, r) {
  ((e = t.state),
    typeof t.componentWillReceiveProps == "function" &&
      t.componentWillReceiveProps(n, r),
    typeof t.UNSAFE_componentWillReceiveProps == "function" &&
      t.UNSAFE_componentWillReceiveProps(n, r),
    t.state !== e && Bl.enqueueReplaceState(t, t.state, null));
}
function Ss(e, t, n, r) {
  var i = e.stateNode;
  ((i.props = n), (i.state = e.memoizedState), (i.refs = {}), Ou(e));
  var o = t.contextType;
  (typeof o == "object" && o !== null
    ? (i.context = yt(o))
    : ((o = et(t) ? Kn : Be.current), (i.context = Mr(e, o))),
    (i.state = e.memoizedState),
    (o = t.getDerivedStateFromProps),
    typeof o == "function" && (ks(e, t, o, n), (i.state = e.memoizedState)),
    typeof t.getDerivedStateFromProps == "function" ||
      typeof i.getSnapshotBeforeUpdate == "function" ||
      (typeof i.UNSAFE_componentWillMount != "function" &&
        typeof i.componentWillMount != "function") ||
      ((t = i.state),
      typeof i.componentWillMount == "function" && i.componentWillMount(),
      typeof i.UNSAFE_componentWillMount == "function" &&
        i.UNSAFE_componentWillMount(),
      t !== i.state && Bl.enqueueReplaceState(i, i.state, null),
      pl(e, n, i, r),
      (i.state = e.memoizedState)),
    typeof i.componentDidMount == "function" && (e.flags |= 4194308));
}
function zr(e, t) {
  try {
    var n = "",
      r = t;
    do ((n += ib(r)), (r = r.return));
    while (r);
    var i = n;
  } catch (o) {
    i =
      `
Error generating stack: ` +
      o.message +
      `
` +
      o.stack;
  }
  return { value: e, source: t, stack: i, digest: null };
}
function _a(e, t, n) {
  return { value: e, source: null, stack: n ?? null, digest: t ?? null };
}
function Ns(e, t) {
  try {
    console.error(t.value);
  } catch (n) {
    setTimeout(function () {
      throw n;
    });
  }
}
var Ov = typeof WeakMap == "function" ? WeakMap : Map;
function Qh(e, t, n) {
  ((n = qt(-1, n)), (n.tag = 3), (n.payload = { element: null }));
  var r = t.value;
  return (
    (n.callback = function () {
      (bl || ((bl = !0), (Ps = r)), Ns(e, t));
    }),
    n
  );
}
function Zh(e, t, n) {
  ((n = qt(-1, n)), (n.tag = 3));
  var r = e.type.getDerivedStateFromError;
  if (typeof r == "function") {
    var i = t.value;
    ((n.payload = function () {
      return r(i);
    }),
      (n.callback = function () {
        Ns(e, t);
      }));
  }
  var o = e.stateNode;
  return (
    o !== null &&
      typeof o.componentDidCatch == "function" &&
      (n.callback = function () {
        (Ns(e, t),
          typeof r != "function" &&
            (_n === null ? (_n = new Set([this])) : _n.add(this)));
        var l = t.stack;
        this.componentDidCatch(t.value, {
          componentStack: l !== null ? l : "",
        });
      }),
    n
  );
}
function bd(e, t, n) {
  var r = e.pingCache;
  if (r === null) {
    r = e.pingCache = new Ov();
    var i = new Set();
    r.set(t, i);
  } else ((i = r.get(t)), i === void 0 && ((i = new Set()), r.set(t, i)));
  i.has(n) || (i.add(n), (e = Gv.bind(null, e, t, n)), t.then(e, e));
}
function vd(e) {
  do {
    var t;
    if (
      ((t = e.tag === 13) &&
        ((t = e.memoizedState), (t = t !== null ? t.dehydrated !== null : !0)),
      t)
    )
      return e;
    e = e.return;
  } while (e !== null);
  return null;
}
function Ed(e, t, n, r, i) {
  return e.mode & 1
    ? ((e.flags |= 65536), (e.lanes = i), e)
    : (e === t
        ? (e.flags |= 65536)
        : ((e.flags |= 128),
          (n.flags |= 131072),
          (n.flags &= -52805),
          n.tag === 1 &&
            (n.alternate === null
              ? (n.tag = 17)
              : ((t = qt(-1, 1)), (t.tag = 2), xn(n, t, 1))),
          (n.lanes |= 1)),
      e);
}
var Iv = en.ReactCurrentOwner,
  Xe = !1;
function We(e, t, n, r) {
  t.child = e === null ? Nh(t, null, n, r) : Dr(t, e.child, n, r);
}
function wd(e, t, n, r, i) {
  n = n.render;
  var o = t.ref;
  return (
    Tr(t, i),
    (r = Pu(e, t, n, r, o, i)),
    (n = zu()),
    e !== null && !Xe
      ? ((t.updateQueue = e.updateQueue),
        (t.flags &= -2053),
        (e.lanes &= ~i),
        Jt(e, t, i))
      : (ye && n && ku(t), (t.flags |= 1), We(e, t, r, i), t.child)
  );
}
function xd(e, t, n, r, i) {
  if (e === null) {
    var o = n.type;
    return typeof o == "function" &&
      !Vu(o) &&
      o.defaultProps === void 0 &&
      n.compare === null &&
      n.defaultProps === void 0
      ? ((t.tag = 15), (t.type = o), Xh(e, t, o, r, i))
      : ((e = Vo(n.type, null, r, t, t.mode, i)),
        (e.ref = t.ref),
        (e.return = t),
        (t.child = e));
  }
  if (((o = e.child), !(e.lanes & i))) {
    var l = o.memoizedProps;
    if (
      ((n = n.compare), (n = n !== null ? n : Di), n(l, r) && e.ref === t.ref)
    )
      return Jt(e, t, i);
  }
  return (
    (t.flags |= 1),
    (e = Sn(o, r)),
    (e.ref = t.ref),
    (e.return = t),
    (t.child = e)
  );
}
function Xh(e, t, n, r, i) {
  if (e !== null) {
    var o = e.memoizedProps;
    if (Di(o, r) && e.ref === t.ref)
      if (((Xe = !1), (t.pendingProps = r = o), (e.lanes & i) !== 0))
        e.flags & 131072 && (Xe = !0);
      else return ((t.lanes = e.lanes), Jt(e, t, i));
  }
  return Cs(e, t, n, r, i);
}
function Jh(e, t, n) {
  var r = t.pendingProps,
    i = r.children,
    o = e !== null ? e.memoizedState : null;
  if (r.mode === "hidden")
    if (!(t.mode & 1))
      ((t.memoizedState = { baseLanes: 0, cachePool: null, transitions: null }),
        fe(_r, ot),
        (ot |= n));
    else {
      if (!(n & 1073741824))
        return (
          (e = o !== null ? o.baseLanes | n : n),
          (t.lanes = t.childLanes = 1073741824),
          (t.memoizedState = {
            baseLanes: e,
            cachePool: null,
            transitions: null,
          }),
          (t.updateQueue = null),
          fe(_r, ot),
          (ot |= e),
          null
        );
      ((t.memoizedState = { baseLanes: 0, cachePool: null, transitions: null }),
        (r = o !== null ? o.baseLanes : n),
        fe(_r, ot),
        (ot |= r));
    }
  else
    (o !== null ? ((r = o.baseLanes | n), (t.memoizedState = null)) : (r = n),
      fe(_r, ot),
      (ot |= r));
  return (We(e, t, i, n), t.child);
}
function eg(e, t) {
  var n = t.ref;
  ((e === null && n !== null) || (e !== null && e.ref !== n)) &&
    ((t.flags |= 512), (t.flags |= 2097152));
}
function Cs(e, t, n, r, i) {
  var o = et(n) ? Kn : Be.current;
  return (
    (o = Mr(t, o)),
    Tr(t, i),
    (n = Pu(e, t, n, r, o, i)),
    (r = zu()),
    e !== null && !Xe
      ? ((t.updateQueue = e.updateQueue),
        (t.flags &= -2053),
        (e.lanes &= ~i),
        Jt(e, t, i))
      : (ye && r && ku(t), (t.flags |= 1), We(e, t, n, i), t.child)
  );
}
function _d(e, t, n, r, i) {
  if (et(n)) {
    var o = !0;
    sl(t);
  } else o = !1;
  if ((Tr(t, i), t.stateNode === null))
    (Wo(e, t), Yh(t, n, r), Ss(t, n, r, i), (r = !0));
  else if (e === null) {
    var l = t.stateNode,
      a = t.memoizedProps;
    l.props = a;
    var s = l.context,
      u = n.contextType;
    typeof u == "object" && u !== null
      ? (u = yt(u))
      : ((u = et(n) ? Kn : Be.current), (u = Mr(t, u)));
    var d = n.getDerivedStateFromProps,
      c =
        typeof d == "function" ||
        typeof l.getSnapshotBeforeUpdate == "function";
    (c ||
      (typeof l.UNSAFE_componentWillReceiveProps != "function" &&
        typeof l.componentWillReceiveProps != "function") ||
      ((a !== r || s !== u) && yd(t, l, r, u)),
      (dn = !1));
    var f = t.memoizedState;
    ((l.state = f),
      pl(t, r, l, i),
      (s = t.memoizedState),
      a !== r || f !== s || Je.current || dn
        ? (typeof d == "function" && (ks(t, n, d, r), (s = t.memoizedState)),
          (a = dn || md(t, n, a, r, f, s, u))
            ? (c ||
                (typeof l.UNSAFE_componentWillMount != "function" &&
                  typeof l.componentWillMount != "function") ||
                (typeof l.componentWillMount == "function" &&
                  l.componentWillMount(),
                typeof l.UNSAFE_componentWillMount == "function" &&
                  l.UNSAFE_componentWillMount()),
              typeof l.componentDidMount == "function" && (t.flags |= 4194308))
            : (typeof l.componentDidMount == "function" && (t.flags |= 4194308),
              (t.memoizedProps = r),
              (t.memoizedState = s)),
          (l.props = r),
          (l.state = s),
          (l.context = u),
          (r = a))
        : (typeof l.componentDidMount == "function" && (t.flags |= 4194308),
          (r = !1)));
  } else {
    ((l = t.stateNode),
      Th(e, t),
      (a = t.memoizedProps),
      (u = t.type === t.elementType ? a : xt(t.type, a)),
      (l.props = u),
      (c = t.pendingProps),
      (f = l.context),
      (s = n.contextType),
      typeof s == "object" && s !== null
        ? (s = yt(s))
        : ((s = et(n) ? Kn : Be.current), (s = Mr(t, s))));
    var p = n.getDerivedStateFromProps;
    ((d =
      typeof p == "function" ||
      typeof l.getSnapshotBeforeUpdate == "function") ||
      (typeof l.UNSAFE_componentWillReceiveProps != "function" &&
        typeof l.componentWillReceiveProps != "function") ||
      ((a !== c || f !== s) && yd(t, l, r, s)),
      (dn = !1),
      (f = t.memoizedState),
      (l.state = f),
      pl(t, r, l, i));
    var g = t.memoizedState;
    a !== c || f !== g || Je.current || dn
      ? (typeof p == "function" && (ks(t, n, p, r), (g = t.memoizedState)),
        (u = dn || md(t, n, u, r, f, g, s) || !1)
          ? (d ||
              (typeof l.UNSAFE_componentWillUpdate != "function" &&
                typeof l.componentWillUpdate != "function") ||
              (typeof l.componentWillUpdate == "function" &&
                l.componentWillUpdate(r, g, s),
              typeof l.UNSAFE_componentWillUpdate == "function" &&
                l.UNSAFE_componentWillUpdate(r, g, s)),
            typeof l.componentDidUpdate == "function" && (t.flags |= 4),
            typeof l.getSnapshotBeforeUpdate == "function" && (t.flags |= 1024))
          : (typeof l.componentDidUpdate != "function" ||
              (a === e.memoizedProps && f === e.memoizedState) ||
              (t.flags |= 4),
            typeof l.getSnapshotBeforeUpdate != "function" ||
              (a === e.memoizedProps && f === e.memoizedState) ||
              (t.flags |= 1024),
            (t.memoizedProps = r),
            (t.memoizedState = g)),
        (l.props = r),
        (l.state = g),
        (l.context = s),
        (r = u))
      : (typeof l.componentDidUpdate != "function" ||
          (a === e.memoizedProps && f === e.memoizedState) ||
          (t.flags |= 4),
        typeof l.getSnapshotBeforeUpdate != "function" ||
          (a === e.memoizedProps && f === e.memoizedState) ||
          (t.flags |= 1024),
        (r = !1));
  }
  return Ts(e, t, n, r, o, i);
}
function Ts(e, t, n, r, i, o) {
  eg(e, t);
  var l = (t.flags & 128) !== 0;
  if (!r && !l) return (i && sd(t, n, !1), Jt(e, t, o));
  ((r = t.stateNode), (Iv.current = t));
  var a =
    l && typeof n.getDerivedStateFromError != "function" ? null : r.render();
  return (
    (t.flags |= 1),
    e !== null && l
      ? ((t.child = Dr(t, e.child, null, o)), (t.child = Dr(t, null, a, o)))
      : We(e, t, a, o),
    (t.memoizedState = r.state),
    i && sd(t, n, !0),
    t.child
  );
}
function tg(e) {
  var t = e.stateNode;
  (t.pendingContext
    ? ad(e, t.pendingContext, t.pendingContext !== t.context)
    : t.context && ad(e, t.context, !1),
    Iu(e, t.containerInfo));
}
function kd(e, t, n, r, i) {
  return (Lr(), Nu(i), (t.flags |= 256), We(e, t, n, r), t.child);
}
var As = { dehydrated: null, treeContext: null, retryLane: 0 };
function Rs(e) {
  return { baseLanes: e, cachePool: null, transitions: null };
}
function ng(e, t, n) {
  var r = t.pendingProps,
    i = be.current,
    o = !1,
    l = (t.flags & 128) !== 0,
    a;
  if (
    ((a = l) ||
      (a = e !== null && e.memoizedState === null ? !1 : (i & 2) !== 0),
    a
      ? ((o = !0), (t.flags &= -129))
      : (e === null || e.memoizedState !== null) && (i |= 1),
    fe(be, i & 1),
    e === null)
  )
    return (
      xs(t),
      (e = t.memoizedState),
      e !== null && ((e = e.dehydrated), e !== null)
        ? (t.mode & 1
            ? e.data === "$!"
              ? (t.lanes = 8)
              : (t.lanes = 1073741824)
            : (t.lanes = 1),
          null)
        : ((l = r.children),
          (e = r.fallback),
          o
            ? ((r = t.mode),
              (o = t.child),
              (l = { mode: "hidden", children: l }),
              !(r & 1) && o !== null
                ? ((o.childLanes = 0), (o.pendingProps = l))
                : (o = Hl(l, r, 0, null)),
              (e = Hn(e, r, n, null)),
              (o.return = t),
              (e.return = t),
              (o.sibling = e),
              (t.child = o),
              (t.child.memoizedState = Rs(n)),
              (t.memoizedState = As),
              e)
            : Uu(t, l))
    );
  if (((i = e.memoizedState), i !== null && ((a = i.dehydrated), a !== null)))
    return Mv(e, t, l, r, a, i, n);
  if (o) {
    ((o = r.fallback), (l = t.mode), (i = e.child), (a = i.sibling));
    var s = { mode: "hidden", children: r.children };
    return (
      !(l & 1) && t.child !== i
        ? ((r = t.child),
          (r.childLanes = 0),
          (r.pendingProps = s),
          (t.deletions = null))
        : ((r = Sn(i, s)), (r.subtreeFlags = i.subtreeFlags & 14680064)),
      a !== null ? (o = Sn(a, o)) : ((o = Hn(o, l, n, null)), (o.flags |= 2)),
      (o.return = t),
      (r.return = t),
      (r.sibling = o),
      (t.child = r),
      (r = o),
      (o = t.child),
      (l = e.child.memoizedState),
      (l =
        l === null
          ? Rs(n)
          : {
              baseLanes: l.baseLanes | n,
              cachePool: null,
              transitions: l.transitions,
            }),
      (o.memoizedState = l),
      (o.childLanes = e.childLanes & ~n),
      (t.memoizedState = As),
      r
    );
  }
  return (
    (o = e.child),
    (e = o.sibling),
    (r = Sn(o, { mode: "visible", children: r.children })),
    !(t.mode & 1) && (r.lanes = n),
    (r.return = t),
    (r.sibling = null),
    e !== null &&
      ((n = t.deletions),
      n === null ? ((t.deletions = [e]), (t.flags |= 16)) : n.push(e)),
    (t.child = r),
    (t.memoizedState = null),
    r
  );
}
function Uu(e, t) {
  return (
    (t = Hl({ mode: "visible", children: t }, e.mode, 0, null)),
    (t.return = e),
    (e.child = t)
  );
}
function xo(e, t, n, r) {
  return (
    r !== null && Nu(r),
    Dr(t, e.child, null, n),
    (e = Uu(t, t.pendingProps.children)),
    (e.flags |= 2),
    (t.memoizedState = null),
    e
  );
}
function Mv(e, t, n, r, i, o, l) {
  if (n)
    return t.flags & 256
      ? ((t.flags &= -257), (r = _a(Error(P(422)))), xo(e, t, l, r))
      : t.memoizedState !== null
        ? ((t.child = e.child), (t.flags |= 128), null)
        : ((o = r.fallback),
          (i = t.mode),
          (r = Hl({ mode: "visible", children: r.children }, i, 0, null)),
          (o = Hn(o, i, l, null)),
          (o.flags |= 2),
          (r.return = t),
          (o.return = t),
          (r.sibling = o),
          (t.child = r),
          t.mode & 1 && Dr(t, e.child, null, l),
          (t.child.memoizedState = Rs(l)),
          (t.memoizedState = As),
          o);
  if (!(t.mode & 1)) return xo(e, t, l, null);
  if (i.data === "$!") {
    if (((r = i.nextSibling && i.nextSibling.dataset), r)) var a = r.dgst;
    return (
      (r = a),
      (o = Error(P(419))),
      (r = _a(o, r, void 0)),
      xo(e, t, l, r)
    );
  }
  if (((a = (l & e.childLanes) !== 0), Xe || a)) {
    if (((r = Oe), r !== null)) {
      switch (l & -l) {
        case 4:
          i = 2;
          break;
        case 16:
          i = 8;
          break;
        case 64:
        case 128:
        case 256:
        case 512:
        case 1024:
        case 2048:
        case 4096:
        case 8192:
        case 16384:
        case 32768:
        case 65536:
        case 131072:
        case 262144:
        case 524288:
        case 1048576:
        case 2097152:
        case 4194304:
        case 8388608:
        case 16777216:
        case 33554432:
        case 67108864:
          i = 32;
          break;
        case 536870912:
          i = 268435456;
          break;
        default:
          i = 0;
      }
      ((i = i & (r.suspendedLanes | l) ? 0 : i),
        i !== 0 &&
          i !== o.retryLane &&
          ((o.retryLane = i), Xt(e, i), Nt(r, e, i, -1)));
    }
    return (Ku(), (r = _a(Error(P(421)))), xo(e, t, l, r));
  }
  return i.data === "$?"
    ? ((t.flags |= 128),
      (t.child = e.child),
      (t = Kv.bind(null, e)),
      (i._reactRetry = t),
      null)
    : ((e = o.treeContext),
      (lt = wn(i.nextSibling)),
      (at = t),
      (ye = !0),
      (kt = null),
      e !== null &&
        ((ft[pt++] = Kt),
        (ft[pt++] = Vt),
        (ft[pt++] = Vn),
        (Kt = e.id),
        (Vt = e.overflow),
        (Vn = t)),
      (t = Uu(t, r.children)),
      (t.flags |= 4096),
      t);
}
function Sd(e, t, n) {
  e.lanes |= t;
  var r = e.alternate;
  (r !== null && (r.lanes |= t), _s(e.return, t, n));
}
function ka(e, t, n, r, i) {
  var o = e.memoizedState;
  o === null
    ? (e.memoizedState = {
        isBackwards: t,
        rendering: null,
        renderingStartTime: 0,
        last: r,
        tail: n,
        tailMode: i,
      })
    : ((o.isBackwards = t),
      (o.rendering = null),
      (o.renderingStartTime = 0),
      (o.last = r),
      (o.tail = n),
      (o.tailMode = i));
}
function rg(e, t, n) {
  var r = t.pendingProps,
    i = r.revealOrder,
    o = r.tail;
  if ((We(e, t, r.children, n), (r = be.current), r & 2))
    ((r = (r & 1) | 2), (t.flags |= 128));
  else {
    if (e !== null && e.flags & 128)
      e: for (e = t.child; e !== null;) {
        if (e.tag === 13) e.memoizedState !== null && Sd(e, n, t);
        else if (e.tag === 19) Sd(e, n, t);
        else if (e.child !== null) {
          ((e.child.return = e), (e = e.child));
          continue;
        }
        if (e === t) break e;
        for (; e.sibling === null;) {
          if (e.return === null || e.return === t) break e;
          e = e.return;
        }
        ((e.sibling.return = e.return), (e = e.sibling));
      }
    r &= 1;
  }
  if ((fe(be, r), !(t.mode & 1))) t.memoizedState = null;
  else
    switch (i) {
      case "forwards":
        for (n = t.child, i = null; n !== null;)
          ((e = n.alternate),
            e !== null && hl(e) === null && (i = n),
            (n = n.sibling));
        ((n = i),
          n === null
            ? ((i = t.child), (t.child = null))
            : ((i = n.sibling), (n.sibling = null)),
          ka(t, !1, i, n, o));
        break;
      case "backwards":
        for (n = null, i = t.child, t.child = null; i !== null;) {
          if (((e = i.alternate), e !== null && hl(e) === null)) {
            t.child = i;
            break;
          }
          ((e = i.sibling), (i.sibling = n), (n = i), (i = e));
        }
        ka(t, !0, n, null, o);
        break;
      case "together":
        ka(t, !1, null, null, void 0);
        break;
      default:
        t.memoizedState = null;
    }
  return t.child;
}
function Wo(e, t) {
  !(t.mode & 1) &&
    e !== null &&
    ((e.alternate = null), (t.alternate = null), (t.flags |= 2));
}
function Jt(e, t, n) {
  if (
    (e !== null && (t.dependencies = e.dependencies),
    (Yn |= t.lanes),
    !(n & t.childLanes))
  )
    return null;
  if (e !== null && t.child !== e.child) throw Error(P(153));
  if (t.child !== null) {
    for (
      e = t.child, n = Sn(e, e.pendingProps), t.child = n, n.return = t;
      e.sibling !== null;
    )
      ((e = e.sibling),
        (n = n.sibling = Sn(e, e.pendingProps)),
        (n.return = t));
    n.sibling = null;
  }
  return t.child;
}
function Lv(e, t, n) {
  switch (t.tag) {
    case 3:
      (tg(t), Lr());
      break;
    case 5:
      Ah(t);
      break;
    case 1:
      et(t.type) && sl(t);
      break;
    case 4:
      Iu(t, t.stateNode.containerInfo);
      break;
    case 10:
      var r = t.type._context,
        i = t.memoizedProps.value;
      (fe(dl, r._currentValue), (r._currentValue = i));
      break;
    case 13:
      if (((r = t.memoizedState), r !== null))
        return r.dehydrated !== null
          ? (fe(be, be.current & 1), (t.flags |= 128), null)
          : n & t.child.childLanes
            ? ng(e, t, n)
            : (fe(be, be.current & 1),
              (e = Jt(e, t, n)),
              e !== null ? e.sibling : null);
      fe(be, be.current & 1);
      break;
    case 19:
      if (((r = (n & t.childLanes) !== 0), e.flags & 128)) {
        if (r) return rg(e, t, n);
        t.flags |= 128;
      }
      if (
        ((i = t.memoizedState),
        i !== null &&
          ((i.rendering = null), (i.tail = null), (i.lastEffect = null)),
        fe(be, be.current),
        r)
      )
        break;
      return null;
    case 22:
    case 23:
      return ((t.lanes = 0), Jh(e, t, n));
  }
  return Jt(e, t, n);
}
var ig, Os, og, lg;
ig = function (e, t) {
  for (var n = t.child; n !== null;) {
    if (n.tag === 5 || n.tag === 6) e.appendChild(n.stateNode);
    else if (n.tag !== 4 && n.child !== null) {
      ((n.child.return = n), (n = n.child));
      continue;
    }
    if (n === t) break;
    for (; n.sibling === null;) {
      if (n.return === null || n.return === t) return;
      n = n.return;
    }
    ((n.sibling.return = n.return), (n = n.sibling));
  }
};
Os = function () {};
og = function (e, t, n, r) {
  var i = e.memoizedProps;
  if (i !== r) {
    ((e = t.stateNode), Un(Ft.current));
    var o = null;
    switch (n) {
      case "input":
        ((i = Ja(e, i)), (r = Ja(e, r)), (o = []));
        break;
      case "select":
        ((i = Ee({}, i, { value: void 0 })),
          (r = Ee({}, r, { value: void 0 })),
          (o = []));
        break;
      case "textarea":
        ((i = ns(e, i)), (r = ns(e, r)), (o = []));
        break;
      default:
        typeof i.onClick != "function" &&
          typeof r.onClick == "function" &&
          (e.onclick = ll);
    }
    is(n, r);
    var l;
    n = null;
    for (u in i)
      if (!r.hasOwnProperty(u) && i.hasOwnProperty(u) && i[u] != null)
        if (u === "style") {
          var a = i[u];
          for (l in a) a.hasOwnProperty(l) && (n || (n = {}), (n[l] = ""));
        } else
          u !== "dangerouslySetInnerHTML" &&
            u !== "children" &&
            u !== "suppressContentEditableWarning" &&
            u !== "suppressHydrationWarning" &&
            u !== "autoFocus" &&
            (Ti.hasOwnProperty(u)
              ? o || (o = [])
              : (o = o || []).push(u, null));
    for (u in r) {
      var s = r[u];
      if (
        ((a = i != null ? i[u] : void 0),
        r.hasOwnProperty(u) && s !== a && (s != null || a != null))
      )
        if (u === "style")
          if (a) {
            for (l in a)
              !a.hasOwnProperty(l) ||
                (s && s.hasOwnProperty(l)) ||
                (n || (n = {}), (n[l] = ""));
            for (l in s)
              s.hasOwnProperty(l) &&
                a[l] !== s[l] &&
                (n || (n = {}), (n[l] = s[l]));
          } else (n || (o || (o = []), o.push(u, n)), (n = s));
        else
          u === "dangerouslySetInnerHTML"
            ? ((s = s ? s.__html : void 0),
              (a = a ? a.__html : void 0),
              s != null && a !== s && (o = o || []).push(u, s))
            : u === "children"
              ? (typeof s != "string" && typeof s != "number") ||
                (o = o || []).push(u, "" + s)
              : u !== "suppressContentEditableWarning" &&
                u !== "suppressHydrationWarning" &&
                (Ti.hasOwnProperty(u)
                  ? (s != null && u === "onScroll" && ge("scroll", e),
                    o || a === s || (o = []))
                  : (o = o || []).push(u, s));
    }
    n && (o = o || []).push("style", n);
    var u = o;
    (t.updateQueue = u) && (t.flags |= 4);
  }
};
lg = function (e, t, n, r) {
  n !== r && (t.flags |= 4);
};
function oi(e, t) {
  if (!ye)
    switch (e.tailMode) {
      case "hidden":
        t = e.tail;
        for (var n = null; t !== null;)
          (t.alternate !== null && (n = t), (t = t.sibling));
        n === null ? (e.tail = null) : (n.sibling = null);
        break;
      case "collapsed":
        n = e.tail;
        for (var r = null; n !== null;)
          (n.alternate !== null && (r = n), (n = n.sibling));
        r === null
          ? t || e.tail === null
            ? (e.tail = null)
            : (e.tail.sibling = null)
          : (r.sibling = null);
    }
}
function Pe(e) {
  var t = e.alternate !== null && e.alternate.child === e.child,
    n = 0,
    r = 0;
  if (t)
    for (var i = e.child; i !== null;)
      ((n |= i.lanes | i.childLanes),
        (r |= i.subtreeFlags & 14680064),
        (r |= i.flags & 14680064),
        (i.return = e),
        (i = i.sibling));
  else
    for (i = e.child; i !== null;)
      ((n |= i.lanes | i.childLanes),
        (r |= i.subtreeFlags),
        (r |= i.flags),
        (i.return = e),
        (i = i.sibling));
  return ((e.subtreeFlags |= r), (e.childLanes = n), t);
}
function Dv(e, t, n) {
  var r = t.pendingProps;
  switch ((Su(t), t.tag)) {
    case 2:
    case 16:
    case 15:
    case 0:
    case 11:
    case 7:
    case 8:
    case 12:
    case 9:
    case 14:
      return (Pe(t), null);
    case 1:
      return (et(t.type) && al(), Pe(t), null);
    case 3:
      return (
        (r = t.stateNode),
        Pr(),
        me(Je),
        me(Be),
        Lu(),
        r.pendingContext &&
          ((r.context = r.pendingContext), (r.pendingContext = null)),
        (e === null || e.child === null) &&
          (Eo(t)
            ? (t.flags |= 4)
            : e === null ||
              (e.memoizedState.isDehydrated && !(t.flags & 256)) ||
              ((t.flags |= 1024), kt !== null && (Bs(kt), (kt = null)))),
        Os(e, t),
        Pe(t),
        null
      );
    case 5:
      Mu(t);
      var i = Un(Ui.current);
      if (((n = t.type), e !== null && t.stateNode != null))
        (og(e, t, n, r, i),
          e.ref !== t.ref && ((t.flags |= 512), (t.flags |= 2097152)));
      else {
        if (!r) {
          if (t.stateNode === null) throw Error(P(166));
          return (Pe(t), null);
        }
        if (((e = Un(Ft.current)), Eo(t))) {
          ((r = t.stateNode), (n = t.type));
          var o = t.memoizedProps;
          switch (((r[Pt] = t), (r[Fi] = o), (e = (t.mode & 1) !== 0), n)) {
            case "dialog":
              (ge("cancel", r), ge("close", r));
              break;
            case "iframe":
            case "object":
            case "embed":
              ge("load", r);
              break;
            case "video":
            case "audio":
              for (i = 0; i < gi.length; i++) ge(gi[i], r);
              break;
            case "source":
              ge("error", r);
              break;
            case "img":
            case "image":
            case "link":
              (ge("error", r), ge("load", r));
              break;
            case "details":
              ge("toggle", r);
              break;
            case "input":
              (Lc(r, o), ge("invalid", r));
              break;
            case "select":
              ((r._wrapperState = { wasMultiple: !!o.multiple }),
                ge("invalid", r));
              break;
            case "textarea":
              (Pc(r, o), ge("invalid", r));
          }
          (is(n, o), (i = null));
          for (var l in o)
            if (o.hasOwnProperty(l)) {
              var a = o[l];
              l === "children"
                ? typeof a == "string"
                  ? r.textContent !== a &&
                    (o.suppressHydrationWarning !== !0 &&
                      vo(r.textContent, a, e),
                    (i = ["children", a]))
                  : typeof a == "number" &&
                    r.textContent !== "" + a &&
                    (o.suppressHydrationWarning !== !0 &&
                      vo(r.textContent, a, e),
                    (i = ["children", "" + a]))
                : Ti.hasOwnProperty(l) &&
                  a != null &&
                  l === "onScroll" &&
                  ge("scroll", r);
            }
          switch (n) {
            case "input":
              (co(r), Dc(r, o, !0));
              break;
            case "textarea":
              (co(r), zc(r));
              break;
            case "select":
            case "option":
              break;
            default:
              typeof o.onClick == "function" && (r.onclick = ll);
          }
          ((r = i), (t.updateQueue = r), r !== null && (t.flags |= 4));
        } else {
          ((l = i.nodeType === 9 ? i : i.ownerDocument),
            e === "http://www.w3.org/1999/xhtml" && (e = Lp(n)),
            e === "http://www.w3.org/1999/xhtml"
              ? n === "script"
                ? ((e = l.createElement("div")),
                  (e.innerHTML = "<script><\/script>"),
                  (e = e.removeChild(e.firstChild)))
                : typeof r.is == "string"
                  ? (e = l.createElement(n, { is: r.is }))
                  : ((e = l.createElement(n)),
                    n === "select" &&
                      ((l = e),
                      r.multiple
                        ? (l.multiple = !0)
                        : r.size && (l.size = r.size)))
              : (e = l.createElementNS(e, n)),
            (e[Pt] = t),
            (e[Fi] = r),
            ig(e, t, !1, !1),
            (t.stateNode = e));
          e: {
            switch (((l = os(n, r)), n)) {
              case "dialog":
                (ge("cancel", e), ge("close", e), (i = r));
                break;
              case "iframe":
              case "object":
              case "embed":
                (ge("load", e), (i = r));
                break;
              case "video":
              case "audio":
                for (i = 0; i < gi.length; i++) ge(gi[i], e);
                i = r;
                break;
              case "source":
                (ge("error", e), (i = r));
                break;
              case "img":
              case "image":
              case "link":
                (ge("error", e), ge("load", e), (i = r));
                break;
              case "details":
                (ge("toggle", e), (i = r));
                break;
              case "input":
                (Lc(e, r), (i = Ja(e, r)), ge("invalid", e));
                break;
              case "option":
                i = r;
                break;
              case "select":
                ((e._wrapperState = { wasMultiple: !!r.multiple }),
                  (i = Ee({}, r, { value: void 0 })),
                  ge("invalid", e));
                break;
              case "textarea":
                (Pc(e, r), (i = ns(e, r)), ge("invalid", e));
                break;
              default:
                i = r;
            }
            (is(n, i), (a = i));
            for (o in a)
              if (a.hasOwnProperty(o)) {
                var s = a[o];
                o === "style"
                  ? zp(e, s)
                  : o === "dangerouslySetInnerHTML"
                    ? ((s = s ? s.__html : void 0), s != null && Dp(e, s))
                    : o === "children"
                      ? typeof s == "string"
                        ? (n !== "textarea" || s !== "") && Ai(e, s)
                        : typeof s == "number" && Ai(e, "" + s)
                      : o !== "suppressContentEditableWarning" &&
                        o !== "suppressHydrationWarning" &&
                        o !== "autoFocus" &&
                        (Ti.hasOwnProperty(o)
                          ? s != null && o === "onScroll" && ge("scroll", e)
                          : s != null && cu(e, o, s, l));
              }
            switch (n) {
              case "input":
                (co(e), Dc(e, r, !1));
                break;
              case "textarea":
                (co(e), zc(e));
                break;
              case "option":
                r.value != null && e.setAttribute("value", "" + Nn(r.value));
                break;
              case "select":
                ((e.multiple = !!r.multiple),
                  (o = r.value),
                  o != null
                    ? kr(e, !!r.multiple, o, !1)
                    : r.defaultValue != null &&
                      kr(e, !!r.multiple, r.defaultValue, !0));
                break;
              default:
                typeof i.onClick == "function" && (e.onclick = ll);
            }
            switch (n) {
              case "button":
              case "input":
              case "select":
              case "textarea":
                r = !!r.autoFocus;
                break e;
              case "img":
                r = !0;
                break e;
              default:
                r = !1;
            }
          }
          r && (t.flags |= 4);
        }
        t.ref !== null && ((t.flags |= 512), (t.flags |= 2097152));
      }
      return (Pe(t), null);
    case 6:
      if (e && t.stateNode != null) lg(e, t, e.memoizedProps, r);
      else {
        if (typeof r != "string" && t.stateNode === null) throw Error(P(166));
        if (((n = Un(Ui.current)), Un(Ft.current), Eo(t))) {
          if (
            ((r = t.stateNode),
            (n = t.memoizedProps),
            (r[Pt] = t),
            (o = r.nodeValue !== n) && ((e = at), e !== null))
          )
            switch (e.tag) {
              case 3:
                vo(r.nodeValue, n, (e.mode & 1) !== 0);
                break;
              case 5:
                e.memoizedProps.suppressHydrationWarning !== !0 &&
                  vo(r.nodeValue, n, (e.mode & 1) !== 0);
            }
          o && (t.flags |= 4);
        } else
          ((r = (n.nodeType === 9 ? n : n.ownerDocument).createTextNode(r)),
            (r[Pt] = t),
            (t.stateNode = r));
      }
      return (Pe(t), null);
    case 13:
      if (
        (me(be),
        (r = t.memoizedState),
        e === null ||
          (e.memoizedState !== null && e.memoizedState.dehydrated !== null))
      ) {
        if (ye && lt !== null && t.mode & 1 && !(t.flags & 128))
          (kh(), Lr(), (t.flags |= 98560), (o = !1));
        else if (((o = Eo(t)), r !== null && r.dehydrated !== null)) {
          if (e === null) {
            if (!o) throw Error(P(318));
            if (
              ((o = t.memoizedState),
              (o = o !== null ? o.dehydrated : null),
              !o)
            )
              throw Error(P(317));
            o[Pt] = t;
          } else
            (Lr(),
              !(t.flags & 128) && (t.memoizedState = null),
              (t.flags |= 4));
          (Pe(t), (o = !1));
        } else (kt !== null && (Bs(kt), (kt = null)), (o = !0));
        if (!o) return t.flags & 65536 ? t : null;
      }
      return t.flags & 128
        ? ((t.lanes = n), t)
        : ((r = r !== null),
          r !== (e !== null && e.memoizedState !== null) &&
            r &&
            ((t.child.flags |= 8192),
            t.mode & 1 &&
              (e === null || be.current & 1 ? Ae === 0 && (Ae = 3) : Ku())),
          t.updateQueue !== null && (t.flags |= 4),
          Pe(t),
          null);
    case 4:
      return (
        Pr(),
        Os(e, t),
        e === null && Pi(t.stateNode.containerInfo),
        Pe(t),
        null
      );
    case 10:
      return (Au(t.type._context), Pe(t), null);
    case 17:
      return (et(t.type) && al(), Pe(t), null);
    case 19:
      if ((me(be), (o = t.memoizedState), o === null)) return (Pe(t), null);
      if (((r = (t.flags & 128) !== 0), (l = o.rendering), l === null))
        if (r) oi(o, !1);
        else {
          if (Ae !== 0 || (e !== null && e.flags & 128))
            for (e = t.child; e !== null;) {
              if (((l = hl(e)), l !== null)) {
                for (
                  t.flags |= 128,
                    oi(o, !1),
                    r = l.updateQueue,
                    r !== null && ((t.updateQueue = r), (t.flags |= 4)),
                    t.subtreeFlags = 0,
                    r = n,
                    n = t.child;
                  n !== null;
                )
                  ((o = n),
                    (e = r),
                    (o.flags &= 14680066),
                    (l = o.alternate),
                    l === null
                      ? ((o.childLanes = 0),
                        (o.lanes = e),
                        (o.child = null),
                        (o.subtreeFlags = 0),
                        (o.memoizedProps = null),
                        (o.memoizedState = null),
                        (o.updateQueue = null),
                        (o.dependencies = null),
                        (o.stateNode = null))
                      : ((o.childLanes = l.childLanes),
                        (o.lanes = l.lanes),
                        (o.child = l.child),
                        (o.subtreeFlags = 0),
                        (o.deletions = null),
                        (o.memoizedProps = l.memoizedProps),
                        (o.memoizedState = l.memoizedState),
                        (o.updateQueue = l.updateQueue),
                        (o.type = l.type),
                        (e = l.dependencies),
                        (o.dependencies =
                          e === null
                            ? null
                            : {
                                lanes: e.lanes,
                                firstContext: e.firstContext,
                              })),
                    (n = n.sibling));
                return (fe(be, (be.current & 1) | 2), t.child);
              }
              e = e.sibling;
            }
          o.tail !== null &&
            _e() > Fr &&
            ((t.flags |= 128), (r = !0), oi(o, !1), (t.lanes = 4194304));
        }
      else {
        if (!r)
          if (((e = hl(l)), e !== null)) {
            if (
              ((t.flags |= 128),
              (r = !0),
              (n = e.updateQueue),
              n !== null && ((t.updateQueue = n), (t.flags |= 4)),
              oi(o, !0),
              o.tail === null && o.tailMode === "hidden" && !l.alternate && !ye)
            )
              return (Pe(t), null);
          } else
            2 * _e() - o.renderingStartTime > Fr &&
              n !== 1073741824 &&
              ((t.flags |= 128), (r = !0), oi(o, !1), (t.lanes = 4194304));
        o.isBackwards
          ? ((l.sibling = t.child), (t.child = l))
          : ((n = o.last),
            n !== null ? (n.sibling = l) : (t.child = l),
            (o.last = l));
      }
      return o.tail !== null
        ? ((t = o.tail),
          (o.rendering = t),
          (o.tail = t.sibling),
          (o.renderingStartTime = _e()),
          (t.sibling = null),
          (n = be.current),
          fe(be, r ? (n & 1) | 2 : n & 1),
          t)
        : (Pe(t), null);
    case 22:
    case 23:
      return (
        Gu(),
        (r = t.memoizedState !== null),
        e !== null && (e.memoizedState !== null) !== r && (t.flags |= 8192),
        r && t.mode & 1
          ? ot & 1073741824 && (Pe(t), t.subtreeFlags & 6 && (t.flags |= 8192))
          : Pe(t),
        null
      );
    case 24:
      return null;
    case 25:
      return null;
  }
  throw Error(P(156, t.tag));
}
function Pv(e, t) {
  switch ((Su(t), t.tag)) {
    case 1:
      return (
        et(t.type) && al(),
        (e = t.flags),
        e & 65536 ? ((t.flags = (e & -65537) | 128), t) : null
      );
    case 3:
      return (
        Pr(),
        me(Je),
        me(Be),
        Lu(),
        (e = t.flags),
        e & 65536 && !(e & 128) ? ((t.flags = (e & -65537) | 128), t) : null
      );
    case 5:
      return (Mu(t), null);
    case 13:
      if (
        (me(be), (e = t.memoizedState), e !== null && e.dehydrated !== null)
      ) {
        if (t.alternate === null) throw Error(P(340));
        Lr();
      }
      return (
        (e = t.flags),
        e & 65536 ? ((t.flags = (e & -65537) | 128), t) : null
      );
    case 19:
      return (me(be), null);
    case 4:
      return (Pr(), null);
    case 10:
      return (Au(t.type._context), null);
    case 22:
    case 23:
      return (Gu(), null);
    case 24:
      return null;
    default:
      return null;
  }
}
var _o = !1,
  ze = !1,
  zv = typeof WeakSet == "function" ? WeakSet : Set,
  j = null;
function xr(e, t) {
  var n = e.ref;
  if (n !== null)
    if (typeof n == "function")
      try {
        n(null);
      } catch (r) {
        we(e, t, r);
      }
    else n.current = null;
}
function Is(e, t, n) {
  try {
    n();
  } catch (r) {
    we(e, t, r);
  }
}
var Nd = !1;
function Fv(e, t) {
  if (((gs = rl), (e = dh()), _u(e))) {
    if ("selectionStart" in e)
      var n = { start: e.selectionStart, end: e.selectionEnd };
    else
      e: {
        n = ((n = e.ownerDocument) && n.defaultView) || window;
        var r = n.getSelection && n.getSelection();
        if (r && r.rangeCount !== 0) {
          n = r.anchorNode;
          var i = r.anchorOffset,
            o = r.focusNode;
          r = r.focusOffset;
          try {
            (n.nodeType, o.nodeType);
          } catch {
            n = null;
            break e;
          }
          var l = 0,
            a = -1,
            s = -1,
            u = 0,
            d = 0,
            c = e,
            f = null;
          t: for (;;) {
            for (
              var p;
              c !== n || (i !== 0 && c.nodeType !== 3) || (a = l + i),
                c !== o || (r !== 0 && c.nodeType !== 3) || (s = l + r),
                c.nodeType === 3 && (l += c.nodeValue.length),
                (p = c.firstChild) !== null;
            )
              ((f = c), (c = p));
            for (;;) {
              if (c === e) break t;
              if (
                (f === n && ++u === i && (a = l),
                f === o && ++d === r && (s = l),
                (p = c.nextSibling) !== null)
              )
                break;
              ((c = f), (f = c.parentNode));
            }
            c = p;
          }
          n = a === -1 || s === -1 ? null : { start: a, end: s };
        } else n = null;
      }
    n = n || { start: 0, end: 0 };
  } else n = null;
  for (ms = { focusedElem: e, selectionRange: n }, rl = !1, j = t; j !== null;)
    if (((t = j), (e = t.child), (t.subtreeFlags & 1028) !== 0 && e !== null))
      ((e.return = t), (j = e));
    else
      for (; j !== null;) {
        t = j;
        try {
          var g = t.alternate;
          if (t.flags & 1024)
            switch (t.tag) {
              case 0:
              case 11:
              case 15:
                break;
              case 1:
                if (g !== null) {
                  var y = g.memoizedProps,
                    E = g.memoizedState,
                    h = t.stateNode,
                    m = h.getSnapshotBeforeUpdate(
                      t.elementType === t.type ? y : xt(t.type, y),
                      E,
                    );
                  h.__reactInternalSnapshotBeforeUpdate = m;
                }
                break;
              case 3:
                var b = t.stateNode.containerInfo;
                b.nodeType === 1
                  ? (b.textContent = "")
                  : b.nodeType === 9 &&
                    b.documentElement &&
                    b.removeChild(b.documentElement);
                break;
              case 5:
              case 6:
              case 4:
              case 17:
                break;
              default:
                throw Error(P(163));
            }
        } catch (_) {
          we(t, t.return, _);
        }
        if (((e = t.sibling), e !== null)) {
          ((e.return = t.return), (j = e));
          break;
        }
        j = t.return;
      }
  return ((g = Nd), (Nd = !1), g);
}
function xi(e, t, n) {
  var r = t.updateQueue;
  if (((r = r !== null ? r.lastEffect : null), r !== null)) {
    var i = (r = r.next);
    do {
      if ((i.tag & e) === e) {
        var o = i.destroy;
        ((i.destroy = void 0), o !== void 0 && Is(t, n, o));
      }
      i = i.next;
    } while (i !== r);
  }
}
function Ul(e, t) {
  if (
    ((t = t.updateQueue), (t = t !== null ? t.lastEffect : null), t !== null)
  ) {
    var n = (t = t.next);
    do {
      if ((n.tag & e) === e) {
        var r = n.create;
        n.destroy = r();
      }
      n = n.next;
    } while (n !== t);
  }
}
function Ms(e) {
  var t = e.ref;
  if (t !== null) {
    var n = e.stateNode;
    switch (e.tag) {
      case 5:
        e = n;
        break;
      default:
        e = n;
    }
    typeof t == "function" ? t(e) : (t.current = e);
  }
}
function ag(e) {
  var t = e.alternate;
  (t !== null && ((e.alternate = null), ag(t)),
    (e.child = null),
    (e.deletions = null),
    (e.sibling = null),
    e.tag === 5 &&
      ((t = e.stateNode),
      t !== null &&
        (delete t[Pt], delete t[Fi], delete t[vs], delete t[Ev], delete t[wv])),
    (e.stateNode = null),
    (e.return = null),
    (e.dependencies = null),
    (e.memoizedProps = null),
    (e.memoizedState = null),
    (e.pendingProps = null),
    (e.stateNode = null),
    (e.updateQueue = null));
}
function sg(e) {
  return e.tag === 5 || e.tag === 3 || e.tag === 4;
}
function Cd(e) {
  e: for (;;) {
    for (; e.sibling === null;) {
      if (e.return === null || sg(e.return)) return null;
      e = e.return;
    }
    for (
      e.sibling.return = e.return, e = e.sibling;
      e.tag !== 5 && e.tag !== 6 && e.tag !== 18;
    ) {
      if (e.flags & 2 || e.child === null || e.tag === 4) continue e;
      ((e.child.return = e), (e = e.child));
    }
    if (!(e.flags & 2)) return e.stateNode;
  }
}
function Ls(e, t, n) {
  var r = e.tag;
  if (r === 5 || r === 6)
    ((e = e.stateNode),
      t
        ? n.nodeType === 8
          ? n.parentNode.insertBefore(e, t)
          : n.insertBefore(e, t)
        : (n.nodeType === 8
            ? ((t = n.parentNode), t.insertBefore(e, n))
            : ((t = n), t.appendChild(e)),
          (n = n._reactRootContainer),
          n != null || t.onclick !== null || (t.onclick = ll)));
  else if (r !== 4 && ((e = e.child), e !== null))
    for (Ls(e, t, n), e = e.sibling; e !== null;)
      (Ls(e, t, n), (e = e.sibling));
}
function Ds(e, t, n) {
  var r = e.tag;
  if (r === 5 || r === 6)
    ((e = e.stateNode), t ? n.insertBefore(e, t) : n.appendChild(e));
  else if (r !== 4 && ((e = e.child), e !== null))
    for (Ds(e, t, n), e = e.sibling; e !== null;)
      (Ds(e, t, n), (e = e.sibling));
}
var Ie = null,
  _t = !1;
function on(e, t, n) {
  for (n = n.child; n !== null;) (ug(e, t, n), (n = n.sibling));
}
function ug(e, t, n) {
  if (zt && typeof zt.onCommitFiberUnmount == "function")
    try {
      zt.onCommitFiberUnmount(Il, n);
    } catch {}
  switch (n.tag) {
    case 5:
      ze || xr(n, t);
    case 6:
      var r = Ie,
        i = _t;
      ((Ie = null),
        on(e, t, n),
        (Ie = r),
        (_t = i),
        Ie !== null &&
          (_t
            ? ((e = Ie),
              (n = n.stateNode),
              e.nodeType === 8 ? e.parentNode.removeChild(n) : e.removeChild(n))
            : Ie.removeChild(n.stateNode)));
      break;
    case 18:
      Ie !== null &&
        (_t
          ? ((e = Ie),
            (n = n.stateNode),
            e.nodeType === 8
              ? ya(e.parentNode, n)
              : e.nodeType === 1 && ya(e, n),
            Mi(e))
          : ya(Ie, n.stateNode));
      break;
    case 4:
      ((r = Ie),
        (i = _t),
        (Ie = n.stateNode.containerInfo),
        (_t = !0),
        on(e, t, n),
        (Ie = r),
        (_t = i));
      break;
    case 0:
    case 11:
    case 14:
    case 15:
      if (
        !ze &&
        ((r = n.updateQueue), r !== null && ((r = r.lastEffect), r !== null))
      ) {
        i = r = r.next;
        do {
          var o = i,
            l = o.destroy;
          ((o = o.tag),
            l !== void 0 && (o & 2 || o & 4) && Is(n, t, l),
            (i = i.next));
        } while (i !== r);
      }
      on(e, t, n);
      break;
    case 1:
      if (
        !ze &&
        (xr(n, t),
        (r = n.stateNode),
        typeof r.componentWillUnmount == "function")
      )
        try {
          ((r.props = n.memoizedProps),
            (r.state = n.memoizedState),
            r.componentWillUnmount());
        } catch (a) {
          we(n, t, a);
        }
      on(e, t, n);
      break;
    case 21:
      on(e, t, n);
      break;
    case 22:
      n.mode & 1
        ? ((ze = (r = ze) || n.memoizedState !== null), on(e, t, n), (ze = r))
        : on(e, t, n);
      break;
    default:
      on(e, t, n);
  }
}
function Td(e) {
  var t = e.updateQueue;
  if (t !== null) {
    e.updateQueue = null;
    var n = e.stateNode;
    (n === null && (n = e.stateNode = new zv()),
      t.forEach(function (r) {
        var i = Vv.bind(null, e, r);
        n.has(r) || (n.add(r), r.then(i, i));
      }));
  }
}
function wt(e, t) {
  var n = t.deletions;
  if (n !== null)
    for (var r = 0; r < n.length; r++) {
      var i = n[r];
      try {
        var o = e,
          l = t,
          a = l;
        e: for (; a !== null;) {
          switch (a.tag) {
            case 5:
              ((Ie = a.stateNode), (_t = !1));
              break e;
            case 3:
              ((Ie = a.stateNode.containerInfo), (_t = !0));
              break e;
            case 4:
              ((Ie = a.stateNode.containerInfo), (_t = !0));
              break e;
          }
          a = a.return;
        }
        if (Ie === null) throw Error(P(160));
        (ug(o, l, i), (Ie = null), (_t = !1));
        var s = i.alternate;
        (s !== null && (s.return = null), (i.return = null));
      } catch (u) {
        we(i, t, u);
      }
    }
  if (t.subtreeFlags & 12854)
    for (t = t.child; t !== null;) (cg(t, e), (t = t.sibling));
}
function cg(e, t) {
  var n = e.alternate,
    r = e.flags;
  switch (e.tag) {
    case 0:
    case 11:
    case 14:
    case 15:
      if ((wt(t, e), It(e), r & 4)) {
        try {
          (xi(3, e, e.return), Ul(3, e));
        } catch (y) {
          we(e, e.return, y);
        }
        try {
          xi(5, e, e.return);
        } catch (y) {
          we(e, e.return, y);
        }
      }
      break;
    case 1:
      (wt(t, e), It(e), r & 512 && n !== null && xr(n, n.return));
      break;
    case 5:
      if (
        (wt(t, e),
        It(e),
        r & 512 && n !== null && xr(n, n.return),
        e.flags & 32)
      ) {
        var i = e.stateNode;
        try {
          Ai(i, "");
        } catch (y) {
          we(e, e.return, y);
        }
      }
      if (r & 4 && ((i = e.stateNode), i != null)) {
        var o = e.memoizedProps,
          l = n !== null ? n.memoizedProps : o,
          a = e.type,
          s = e.updateQueue;
        if (((e.updateQueue = null), s !== null))
          try {
            (a === "input" && o.type === "radio" && o.name != null && Ip(i, o),
              os(a, l));
            var u = os(a, o);
            for (l = 0; l < s.length; l += 2) {
              var d = s[l],
                c = s[l + 1];
              d === "style"
                ? zp(i, c)
                : d === "dangerouslySetInnerHTML"
                  ? Dp(i, c)
                  : d === "children"
                    ? Ai(i, c)
                    : cu(i, d, c, u);
            }
            switch (a) {
              case "input":
                es(i, o);
                break;
              case "textarea":
                Mp(i, o);
                break;
              case "select":
                var f = i._wrapperState.wasMultiple;
                i._wrapperState.wasMultiple = !!o.multiple;
                var p = o.value;
                p != null
                  ? kr(i, !!o.multiple, p, !1)
                  : f !== !!o.multiple &&
                    (o.defaultValue != null
                      ? kr(i, !!o.multiple, o.defaultValue, !0)
                      : kr(i, !!o.multiple, o.multiple ? [] : "", !1));
            }
            i[Fi] = o;
          } catch (y) {
            we(e, e.return, y);
          }
      }
      break;
    case 6:
      if ((wt(t, e), It(e), r & 4)) {
        if (e.stateNode === null) throw Error(P(162));
        ((i = e.stateNode), (o = e.memoizedProps));
        try {
          i.nodeValue = o;
        } catch (y) {
          we(e, e.return, y);
        }
      }
      break;
    case 3:
      if (
        (wt(t, e), It(e), r & 4 && n !== null && n.memoizedState.isDehydrated)
      )
        try {
          Mi(t.containerInfo);
        } catch (y) {
          we(e, e.return, y);
        }
      break;
    case 4:
      (wt(t, e), It(e));
      break;
    case 13:
      (wt(t, e),
        It(e),
        (i = e.child),
        i.flags & 8192 &&
          ((o = i.memoizedState !== null),
          (i.stateNode.isHidden = o),
          !o ||
            (i.alternate !== null && i.alternate.memoizedState !== null) ||
            (ju = _e())),
        r & 4 && Td(e));
      break;
    case 22:
      if (
        ((d = n !== null && n.memoizedState !== null),
        e.mode & 1 ? ((ze = (u = ze) || d), wt(t, e), (ze = u)) : wt(t, e),
        It(e),
        r & 8192)
      ) {
        if (
          ((u = e.memoizedState !== null),
          (e.stateNode.isHidden = u) && !d && e.mode & 1)
        )
          for (j = e, d = e.child; d !== null;) {
            for (c = j = d; j !== null;) {
              switch (((f = j), (p = f.child), f.tag)) {
                case 0:
                case 11:
                case 14:
                case 15:
                  xi(4, f, f.return);
                  break;
                case 1:
                  xr(f, f.return);
                  var g = f.stateNode;
                  if (typeof g.componentWillUnmount == "function") {
                    ((r = f), (n = f.return));
                    try {
                      ((t = r),
                        (g.props = t.memoizedProps),
                        (g.state = t.memoizedState),
                        g.componentWillUnmount());
                    } catch (y) {
                      we(r, n, y);
                    }
                  }
                  break;
                case 5:
                  xr(f, f.return);
                  break;
                case 22:
                  if (f.memoizedState !== null) {
                    Rd(c);
                    continue;
                  }
              }
              p !== null ? ((p.return = f), (j = p)) : Rd(c);
            }
            d = d.sibling;
          }
        e: for (d = null, c = e; ;) {
          if (c.tag === 5) {
            if (d === null) {
              d = c;
              try {
                ((i = c.stateNode),
                  u
                    ? ((o = i.style),
                      typeof o.setProperty == "function"
                        ? o.setProperty("display", "none", "important")
                        : (o.display = "none"))
                    : ((a = c.stateNode),
                      (s = c.memoizedProps.style),
                      (l =
                        s != null && s.hasOwnProperty("display")
                          ? s.display
                          : null),
                      (a.style.display = Pp("display", l))));
              } catch (y) {
                we(e, e.return, y);
              }
            }
          } else if (c.tag === 6) {
            if (d === null)
              try {
                c.stateNode.nodeValue = u ? "" : c.memoizedProps;
              } catch (y) {
                we(e, e.return, y);
              }
          } else if (
            ((c.tag !== 22 && c.tag !== 23) ||
              c.memoizedState === null ||
              c === e) &&
            c.child !== null
          ) {
            ((c.child.return = c), (c = c.child));
            continue;
          }
          if (c === e) break e;
          for (; c.sibling === null;) {
            if (c.return === null || c.return === e) break e;
            (d === c && (d = null), (c = c.return));
          }
          (d === c && (d = null),
            (c.sibling.return = c.return),
            (c = c.sibling));
        }
      }
      break;
    case 19:
      (wt(t, e), It(e), r & 4 && Td(e));
      break;
    case 21:
      break;
    default:
      (wt(t, e), It(e));
  }
}
function It(e) {
  var t = e.flags;
  if (t & 2) {
    try {
      e: {
        for (var n = e.return; n !== null;) {
          if (sg(n)) {
            var r = n;
            break e;
          }
          n = n.return;
        }
        throw Error(P(160));
      }
      switch (r.tag) {
        case 5:
          var i = r.stateNode;
          r.flags & 32 && (Ai(i, ""), (r.flags &= -33));
          var o = Cd(e);
          Ds(e, o, i);
          break;
        case 3:
        case 4:
          var l = r.stateNode.containerInfo,
            a = Cd(e);
          Ls(e, a, l);
          break;
        default:
          throw Error(P(161));
      }
    } catch (s) {
      we(e, e.return, s);
    }
    e.flags &= -3;
  }
  t & 4096 && (e.flags &= -4097);
}
function Bv(e, t, n) {
  ((j = e), dg(e));
}
function dg(e, t, n) {
  for (var r = (e.mode & 1) !== 0; j !== null;) {
    var i = j,
      o = i.child;
    if (i.tag === 22 && r) {
      var l = i.memoizedState !== null || _o;
      if (!l) {
        var a = i.alternate,
          s = (a !== null && a.memoizedState !== null) || ze;
        a = _o;
        var u = ze;
        if (((_o = l), (ze = s) && !u))
          for (j = i; j !== null;)
            ((l = j),
              (s = l.child),
              l.tag === 22 && l.memoizedState !== null
                ? Od(i)
                : s !== null
                  ? ((s.return = l), (j = s))
                  : Od(i));
        for (; o !== null;) ((j = o), dg(o), (o = o.sibling));
        ((j = i), (_o = a), (ze = u));
      }
      Ad(e);
    } else
      i.subtreeFlags & 8772 && o !== null ? ((o.return = i), (j = o)) : Ad(e);
  }
}
function Ad(e) {
  for (; j !== null;) {
    var t = j;
    if (t.flags & 8772) {
      var n = t.alternate;
      try {
        if (t.flags & 8772)
          switch (t.tag) {
            case 0:
            case 11:
            case 15:
              ze || Ul(5, t);
              break;
            case 1:
              var r = t.stateNode;
              if (t.flags & 4 && !ze)
                if (n === null) r.componentDidMount();
                else {
                  var i =
                    t.elementType === t.type
                      ? n.memoizedProps
                      : xt(t.type, n.memoizedProps);
                  r.componentDidUpdate(
                    i,
                    n.memoizedState,
                    r.__reactInternalSnapshotBeforeUpdate,
                  );
                }
              var o = t.updateQueue;
              o !== null && pd(t, o, r);
              break;
            case 3:
              var l = t.updateQueue;
              if (l !== null) {
                if (((n = null), t.child !== null))
                  switch (t.child.tag) {
                    case 5:
                      n = t.child.stateNode;
                      break;
                    case 1:
                      n = t.child.stateNode;
                  }
                pd(t, l, n);
              }
              break;
            case 5:
              var a = t.stateNode;
              if (n === null && t.flags & 4) {
                n = a;
                var s = t.memoizedProps;
                switch (t.type) {
                  case "button":
                  case "input":
                  case "select":
                  case "textarea":
                    s.autoFocus && n.focus();
                    break;
                  case "img":
                    s.src && (n.src = s.src);
                }
              }
              break;
            case 6:
              break;
            case 4:
              break;
            case 12:
              break;
            case 13:
              if (t.memoizedState === null) {
                var u = t.alternate;
                if (u !== null) {
                  var d = u.memoizedState;
                  if (d !== null) {
                    var c = d.dehydrated;
                    c !== null && Mi(c);
                  }
                }
              }
              break;
            case 19:
            case 17:
            case 21:
            case 22:
            case 23:
            case 25:
              break;
            default:
              throw Error(P(163));
          }
        ze || (t.flags & 512 && Ms(t));
      } catch (f) {
        we(t, t.return, f);
      }
    }
    if (t === e) {
      j = null;
      break;
    }
    if (((n = t.sibling), n !== null)) {
      ((n.return = t.return), (j = n));
      break;
    }
    j = t.return;
  }
}
function Rd(e) {
  for (; j !== null;) {
    var t = j;
    if (t === e) {
      j = null;
      break;
    }
    var n = t.sibling;
    if (n !== null) {
      ((n.return = t.return), (j = n));
      break;
    }
    j = t.return;
  }
}
function Od(e) {
  for (; j !== null;) {
    var t = j;
    try {
      switch (t.tag) {
        case 0:
        case 11:
        case 15:
          var n = t.return;
          try {
            Ul(4, t);
          } catch (s) {
            we(t, n, s);
          }
          break;
        case 1:
          var r = t.stateNode;
          if (typeof r.componentDidMount == "function") {
            var i = t.return;
            try {
              r.componentDidMount();
            } catch (s) {
              we(t, i, s);
            }
          }
          var o = t.return;
          try {
            Ms(t);
          } catch (s) {
            we(t, o, s);
          }
          break;
        case 5:
          var l = t.return;
          try {
            Ms(t);
          } catch (s) {
            we(t, l, s);
          }
      }
    } catch (s) {
      we(t, t.return, s);
    }
    if (t === e) {
      j = null;
      break;
    }
    var a = t.sibling;
    if (a !== null) {
      ((a.return = t.return), (j = a));
      break;
    }
    j = t.return;
  }
}
var Uv = Math.ceil,
  yl = en.ReactCurrentDispatcher,
  $u = en.ReactCurrentOwner,
  mt = en.ReactCurrentBatchConfig,
  ie = 0,
  Oe = null,
  Ne = null,
  Me = 0,
  ot = 0,
  _r = An(0),
  Ae = 0,
  Wi = null,
  Yn = 0,
  $l = 0,
  Hu = 0,
  _i = null,
  Ze = null,
  ju = 0,
  Fr = 1 / 0,
  Wt = null,
  bl = !1,
  Ps = null,
  _n = null,
  ko = !1,
  gn = null,
  vl = 0,
  ki = 0,
  zs = null,
  Go = -1,
  Ko = 0;
function Ke() {
  return ie & 6 ? _e() : Go !== -1 ? Go : (Go = _e());
}
function kn(e) {
  return e.mode & 1
    ? ie & 2 && Me !== 0
      ? Me & -Me
      : _v.transition !== null
        ? (Ko === 0 && (Ko = Yp()), Ko)
        : ((e = ae),
          e !== 0 || ((e = window.event), (e = e === void 0 ? 16 : nh(e.type))),
          e)
    : 1;
}
function Nt(e, t, n, r) {
  if (50 < ki) throw ((ki = 0), (zs = null), Error(P(185)));
  (Xi(e, n, r),
    (!(ie & 2) || e !== Oe) &&
      (e === Oe && (!(ie & 2) && ($l |= n), Ae === 4 && pn(e, Me)),
      tt(e, r),
      n === 1 && ie === 0 && !(t.mode & 1) && ((Fr = _e() + 500), zl && Rn())));
}
function tt(e, t) {
  var n = e.callbackNode;
  _b(e, t);
  var r = nl(e, e === Oe ? Me : 0);
  if (r === 0)
    (n !== null && Uc(n), (e.callbackNode = null), (e.callbackPriority = 0));
  else if (((t = r & -r), e.callbackPriority !== t)) {
    if ((n != null && Uc(n), t === 1))
      (e.tag === 0 ? xv(Id.bind(null, e)) : wh(Id.bind(null, e)),
        bv(function () {
          !(ie & 6) && Rn();
        }),
        (n = null));
    else {
      switch (Qp(r)) {
        case 1:
          n = gu;
          break;
        case 4:
          n = Vp;
          break;
        case 16:
          n = tl;
          break;
        case 536870912:
          n = qp;
          break;
        default:
          n = tl;
      }
      n = vg(n, fg.bind(null, e));
    }
    ((e.callbackPriority = t), (e.callbackNode = n));
  }
}
function fg(e, t) {
  if (((Go = -1), (Ko = 0), ie & 6)) throw Error(P(327));
  var n = e.callbackNode;
  if (Ar() && e.callbackNode !== n) return null;
  var r = nl(e, e === Oe ? Me : 0);
  if (r === 0) return null;
  if (r & 30 || r & e.expiredLanes || t) t = El(e, r);
  else {
    t = r;
    var i = ie;
    ie |= 2;
    var o = hg();
    (Oe !== e || Me !== t) && ((Wt = null), (Fr = _e() + 500), $n(e, t));
    do
      try {
        jv();
        break;
      } catch (a) {
        pg(e, a);
      }
    while (!0);
    (Tu(),
      (yl.current = o),
      (ie = i),
      Ne !== null ? (t = 0) : ((Oe = null), (Me = 0), (t = Ae)));
  }
  if (t !== 0) {
    if (
      (t === 2 && ((i = cs(e)), i !== 0 && ((r = i), (t = Fs(e, i)))), t === 1)
    )
      throw ((n = Wi), $n(e, 0), pn(e, r), tt(e, _e()), n);
    if (t === 6) pn(e, r);
    else {
      if (
        ((i = e.current.alternate),
        !(r & 30) &&
          !$v(i) &&
          ((t = El(e, r)),
          t === 2 && ((o = cs(e)), o !== 0 && ((r = o), (t = Fs(e, o)))),
          t === 1))
      )
        throw ((n = Wi), $n(e, 0), pn(e, r), tt(e, _e()), n);
      switch (((e.finishedWork = i), (e.finishedLanes = r), t)) {
        case 0:
        case 1:
          throw Error(P(345));
        case 2:
          Dn(e, Ze, Wt);
          break;
        case 3:
          if (
            (pn(e, r), (r & 130023424) === r && ((t = ju + 500 - _e()), 10 < t))
          ) {
            if (nl(e, 0) !== 0) break;
            if (((i = e.suspendedLanes), (i & r) !== r)) {
              (Ke(), (e.pingedLanes |= e.suspendedLanes & i));
              break;
            }
            e.timeoutHandle = bs(Dn.bind(null, e, Ze, Wt), t);
            break;
          }
          Dn(e, Ze, Wt);
          break;
        case 4:
          if ((pn(e, r), (r & 4194240) === r)) break;
          for (t = e.eventTimes, i = -1; 0 < r;) {
            var l = 31 - St(r);
            ((o = 1 << l), (l = t[l]), l > i && (i = l), (r &= ~o));
          }
          if (
            ((r = i),
            (r = _e() - r),
            (r =
              (120 > r
                ? 120
                : 480 > r
                  ? 480
                  : 1080 > r
                    ? 1080
                    : 1920 > r
                      ? 1920
                      : 3e3 > r
                        ? 3e3
                        : 4320 > r
                          ? 4320
                          : 1960 * Uv(r / 1960)) - r),
            10 < r)
          ) {
            e.timeoutHandle = bs(Dn.bind(null, e, Ze, Wt), r);
            break;
          }
          Dn(e, Ze, Wt);
          break;
        case 5:
          Dn(e, Ze, Wt);
          break;
        default:
          throw Error(P(329));
      }
    }
  }
  return (tt(e, _e()), e.callbackNode === n ? fg.bind(null, e) : null);
}
function Fs(e, t) {
  var n = _i;
  return (
    e.current.memoizedState.isDehydrated && ($n(e, t).flags |= 256),
    (e = El(e, t)),
    e !== 2 && ((t = Ze), (Ze = n), t !== null && Bs(t)),
    e
  );
}
function Bs(e) {
  Ze === null ? (Ze = e) : Ze.push.apply(Ze, e);
}
function $v(e) {
  for (var t = e; ;) {
    if (t.flags & 16384) {
      var n = t.updateQueue;
      if (n !== null && ((n = n.stores), n !== null))
        for (var r = 0; r < n.length; r++) {
          var i = n[r],
            o = i.getSnapshot;
          i = i.value;
          try {
            if (!Tt(o(), i)) return !1;
          } catch {
            return !1;
          }
        }
    }
    if (((n = t.child), t.subtreeFlags & 16384 && n !== null))
      ((n.return = t), (t = n));
    else {
      if (t === e) break;
      for (; t.sibling === null;) {
        if (t.return === null || t.return === e) return !0;
        t = t.return;
      }
      ((t.sibling.return = t.return), (t = t.sibling));
    }
  }
  return !0;
}
function pn(e, t) {
  for (
    t &= ~Hu,
      t &= ~$l,
      e.suspendedLanes |= t,
      e.pingedLanes &= ~t,
      e = e.expirationTimes;
    0 < t;
  ) {
    var n = 31 - St(t),
      r = 1 << n;
    ((e[n] = -1), (t &= ~r));
  }
}
function Id(e) {
  if (ie & 6) throw Error(P(327));
  Ar();
  var t = nl(e, 0);
  if (!(t & 1)) return (tt(e, _e()), null);
  var n = El(e, t);
  if (e.tag !== 0 && n === 2) {
    var r = cs(e);
    r !== 0 && ((t = r), (n = Fs(e, r)));
  }
  if (n === 1) throw ((n = Wi), $n(e, 0), pn(e, t), tt(e, _e()), n);
  if (n === 6) throw Error(P(345));
  return (
    (e.finishedWork = e.current.alternate),
    (e.finishedLanes = t),
    Dn(e, Ze, Wt),
    tt(e, _e()),
    null
  );
}
function Wu(e, t) {
  var n = ie;
  ie |= 1;
  try {
    return e(t);
  } finally {
    ((ie = n), ie === 0 && ((Fr = _e() + 500), zl && Rn()));
  }
}
function Qn(e) {
  gn !== null && gn.tag === 0 && !(ie & 6) && Ar();
  var t = ie;
  ie |= 1;
  var n = mt.transition,
    r = ae;
  try {
    if (((mt.transition = null), (ae = 1), e)) return e();
  } finally {
    ((ae = r), (mt.transition = n), (ie = t), !(ie & 6) && Rn());
  }
}
function Gu() {
  ((ot = _r.current), me(_r));
}
function $n(e, t) {
  ((e.finishedWork = null), (e.finishedLanes = 0));
  var n = e.timeoutHandle;
  if ((n !== -1 && ((e.timeoutHandle = -1), yv(n)), Ne !== null))
    for (n = Ne.return; n !== null;) {
      var r = n;
      switch ((Su(r), r.tag)) {
        case 1:
          ((r = r.type.childContextTypes), r != null && al());
          break;
        case 3:
          (Pr(), me(Je), me(Be), Lu());
          break;
        case 5:
          Mu(r);
          break;
        case 4:
          Pr();
          break;
        case 13:
          me(be);
          break;
        case 19:
          me(be);
          break;
        case 10:
          Au(r.type._context);
          break;
        case 22:
        case 23:
          Gu();
      }
      n = n.return;
    }
  if (
    ((Oe = e),
    (Ne = e = Sn(e.current, null)),
    (Me = ot = t),
    (Ae = 0),
    (Wi = null),
    (Hu = $l = Yn = 0),
    (Ze = _i = null),
    Bn !== null)
  ) {
    for (t = 0; t < Bn.length; t++)
      if (((n = Bn[t]), (r = n.interleaved), r !== null)) {
        n.interleaved = null;
        var i = r.next,
          o = n.pending;
        if (o !== null) {
          var l = o.next;
          ((o.next = i), (r.next = l));
        }
        n.pending = r;
      }
    Bn = null;
  }
  return e;
}
function pg(e, t) {
  do {
    var n = Ne;
    try {
      if ((Tu(), (Ho.current = ml), gl)) {
        for (var r = ve.memoizedState; r !== null;) {
          var i = r.queue;
          (i !== null && (i.pending = null), (r = r.next));
        }
        gl = !1;
      }
      if (
        ((qn = 0),
        (Re = Te = ve = null),
        (wi = !1),
        ($i = 0),
        ($u.current = null),
        n === null || n.return === null)
      ) {
        ((Ae = 1), (Wi = t), (Ne = null));
        break;
      }
      e: {
        var o = e,
          l = n.return,
          a = n,
          s = t;
        if (
          ((t = Me),
          (a.flags |= 32768),
          s !== null && typeof s == "object" && typeof s.then == "function")
        ) {
          var u = s,
            d = a,
            c = d.tag;
          if (!(d.mode & 1) && (c === 0 || c === 11 || c === 15)) {
            var f = d.alternate;
            f
              ? ((d.updateQueue = f.updateQueue),
                (d.memoizedState = f.memoizedState),
                (d.lanes = f.lanes))
              : ((d.updateQueue = null), (d.memoizedState = null));
          }
          var p = vd(l);
          if (p !== null) {
            ((p.flags &= -257),
              Ed(p, l, a, o, t),
              p.mode & 1 && bd(o, u, t),
              (t = p),
              (s = u));
            var g = t.updateQueue;
            if (g === null) {
              var y = new Set();
              (y.add(s), (t.updateQueue = y));
            } else g.add(s);
            break e;
          } else {
            if (!(t & 1)) {
              (bd(o, u, t), Ku());
              break e;
            }
            s = Error(P(426));
          }
        } else if (ye && a.mode & 1) {
          var E = vd(l);
          if (E !== null) {
            (!(E.flags & 65536) && (E.flags |= 256),
              Ed(E, l, a, o, t),
              Nu(zr(s, a)));
            break e;
          }
        }
        ((o = s = zr(s, a)),
          Ae !== 4 && (Ae = 2),
          _i === null ? (_i = [o]) : _i.push(o),
          (o = l));
        do {
          switch (o.tag) {
            case 3:
              ((o.flags |= 65536), (t &= -t), (o.lanes |= t));
              var h = Qh(o, s, t);
              fd(o, h);
              break e;
            case 1:
              a = s;
              var m = o.type,
                b = o.stateNode;
              if (
                !(o.flags & 128) &&
                (typeof m.getDerivedStateFromError == "function" ||
                  (b !== null &&
                    typeof b.componentDidCatch == "function" &&
                    (_n === null || !_n.has(b))))
              ) {
                ((o.flags |= 65536), (t &= -t), (o.lanes |= t));
                var _ = Zh(o, a, t);
                fd(o, _);
                break e;
              }
          }
          o = o.return;
        } while (o !== null);
      }
      mg(n);
    } catch (N) {
      ((t = N), Ne === n && n !== null && (Ne = n = n.return));
      continue;
    }
    break;
  } while (!0);
}
function hg() {
  var e = yl.current;
  return ((yl.current = ml), e === null ? ml : e);
}
function Ku() {
  ((Ae === 0 || Ae === 3 || Ae === 2) && (Ae = 4),
    Oe === null || (!(Yn & 268435455) && !($l & 268435455)) || pn(Oe, Me));
}
function El(e, t) {
  var n = ie;
  ie |= 2;
  var r = hg();
  (Oe !== e || Me !== t) && ((Wt = null), $n(e, t));
  do
    try {
      Hv();
      break;
    } catch (i) {
      pg(e, i);
    }
  while (!0);
  if ((Tu(), (ie = n), (yl.current = r), Ne !== null)) throw Error(P(261));
  return ((Oe = null), (Me = 0), Ae);
}
function Hv() {
  for (; Ne !== null;) gg(Ne);
}
function jv() {
  for (; Ne !== null && !hb();) gg(Ne);
}
function gg(e) {
  var t = bg(e.alternate, e, ot);
  ((e.memoizedProps = e.pendingProps),
    t === null ? mg(e) : (Ne = t),
    ($u.current = null));
}
function mg(e) {
  var t = e;
  do {
    var n = t.alternate;
    if (((e = t.return), t.flags & 32768)) {
      if (((n = Pv(n, t)), n !== null)) {
        ((n.flags &= 32767), (Ne = n));
        return;
      }
      if (e !== null)
        ((e.flags |= 32768), (e.subtreeFlags = 0), (e.deletions = null));
      else {
        ((Ae = 6), (Ne = null));
        return;
      }
    } else if (((n = Dv(n, t, ot)), n !== null)) {
      Ne = n;
      return;
    }
    if (((t = t.sibling), t !== null)) {
      Ne = t;
      return;
    }
    Ne = t = e;
  } while (t !== null);
  Ae === 0 && (Ae = 5);
}
function Dn(e, t, n) {
  var r = ae,
    i = mt.transition;
  try {
    ((mt.transition = null), (ae = 1), Wv(e, t, n, r));
  } finally {
    ((mt.transition = i), (ae = r));
  }
  return null;
}
function Wv(e, t, n, r) {
  do Ar();
  while (gn !== null);
  if (ie & 6) throw Error(P(327));
  n = e.finishedWork;
  var i = e.finishedLanes;
  if (n === null) return null;
  if (((e.finishedWork = null), (e.finishedLanes = 0), n === e.current))
    throw Error(P(177));
  ((e.callbackNode = null), (e.callbackPriority = 0));
  var o = n.lanes | n.childLanes;
  if (
    (kb(e, o),
    e === Oe && ((Ne = Oe = null), (Me = 0)),
    (!(n.subtreeFlags & 2064) && !(n.flags & 2064)) ||
      ko ||
      ((ko = !0),
      vg(tl, function () {
        return (Ar(), null);
      })),
    (o = (n.flags & 15990) !== 0),
    n.subtreeFlags & 15990 || o)
  ) {
    ((o = mt.transition), (mt.transition = null));
    var l = ae;
    ae = 1;
    var a = ie;
    ((ie |= 4),
      ($u.current = null),
      Fv(e, n),
      cg(n, e),
      cv(ms),
      (rl = !!gs),
      (ms = gs = null),
      (e.current = n),
      Bv(n),
      gb(),
      (ie = a),
      (ae = l),
      (mt.transition = o));
  } else e.current = n;
  if (
    (ko && ((ko = !1), (gn = e), (vl = i)),
    (o = e.pendingLanes),
    o === 0 && (_n = null),
    bb(n.stateNode),
    tt(e, _e()),
    t !== null)
  )
    for (r = e.onRecoverableError, n = 0; n < t.length; n++)
      ((i = t[n]), r(i.value, { componentStack: i.stack, digest: i.digest }));
  if (bl) throw ((bl = !1), (e = Ps), (Ps = null), e);
  return (
    vl & 1 && e.tag !== 0 && Ar(),
    (o = e.pendingLanes),
    o & 1 ? (e === zs ? ki++ : ((ki = 0), (zs = e))) : (ki = 0),
    Rn(),
    null
  );
}
function Ar() {
  if (gn !== null) {
    var e = Qp(vl),
      t = mt.transition,
      n = ae;
    try {
      if (((mt.transition = null), (ae = 16 > e ? 16 : e), gn === null))
        var r = !1;
      else {
        if (((e = gn), (gn = null), (vl = 0), ie & 6)) throw Error(P(331));
        var i = ie;
        for (ie |= 4, j = e.current; j !== null;) {
          var o = j,
            l = o.child;
          if (j.flags & 16) {
            var a = o.deletions;
            if (a !== null) {
              for (var s = 0; s < a.length; s++) {
                var u = a[s];
                for (j = u; j !== null;) {
                  var d = j;
                  switch (d.tag) {
                    case 0:
                    case 11:
                    case 15:
                      xi(8, d, o);
                  }
                  var c = d.child;
                  if (c !== null) ((c.return = d), (j = c));
                  else
                    for (; j !== null;) {
                      d = j;
                      var f = d.sibling,
                        p = d.return;
                      if ((ag(d), d === u)) {
                        j = null;
                        break;
                      }
                      if (f !== null) {
                        ((f.return = p), (j = f));
                        break;
                      }
                      j = p;
                    }
                }
              }
              var g = o.alternate;
              if (g !== null) {
                var y = g.child;
                if (y !== null) {
                  g.child = null;
                  do {
                    var E = y.sibling;
                    ((y.sibling = null), (y = E));
                  } while (y !== null);
                }
              }
              j = o;
            }
          }
          if (o.subtreeFlags & 2064 && l !== null) ((l.return = o), (j = l));
          else
            e: for (; j !== null;) {
              if (((o = j), o.flags & 2048))
                switch (o.tag) {
                  case 0:
                  case 11:
                  case 15:
                    xi(9, o, o.return);
                }
              var h = o.sibling;
              if (h !== null) {
                ((h.return = o.return), (j = h));
                break e;
              }
              j = o.return;
            }
        }
        var m = e.current;
        for (j = m; j !== null;) {
          l = j;
          var b = l.child;
          if (l.subtreeFlags & 2064 && b !== null) ((b.return = l), (j = b));
          else
            e: for (l = m; j !== null;) {
              if (((a = j), a.flags & 2048))
                try {
                  switch (a.tag) {
                    case 0:
                    case 11:
                    case 15:
                      Ul(9, a);
                  }
                } catch (N) {
                  we(a, a.return, N);
                }
              if (a === l) {
                j = null;
                break e;
              }
              var _ = a.sibling;
              if (_ !== null) {
                ((_.return = a.return), (j = _));
                break e;
              }
              j = a.return;
            }
        }
        if (
          ((ie = i), Rn(), zt && typeof zt.onPostCommitFiberRoot == "function")
        )
          try {
            zt.onPostCommitFiberRoot(Il, e);
          } catch {}
        r = !0;
      }
      return r;
    } finally {
      ((ae = n), (mt.transition = t));
    }
  }
  return !1;
}
function Md(e, t, n) {
  ((t = zr(n, t)),
    (t = Qh(e, t, 1)),
    (e = xn(e, t, 1)),
    (t = Ke()),
    e !== null && (Xi(e, 1, t), tt(e, t)));
}
function we(e, t, n) {
  if (e.tag === 3) Md(e, e, n);
  else
    for (; t !== null;) {
      if (t.tag === 3) {
        Md(t, e, n);
        break;
      } else if (t.tag === 1) {
        var r = t.stateNode;
        if (
          typeof t.type.getDerivedStateFromError == "function" ||
          (typeof r.componentDidCatch == "function" &&
            (_n === null || !_n.has(r)))
        ) {
          ((e = zr(n, e)),
            (e = Zh(t, e, 1)),
            (t = xn(t, e, 1)),
            (e = Ke()),
            t !== null && (Xi(t, 1, e), tt(t, e)));
          break;
        }
      }
      t = t.return;
    }
}
function Gv(e, t, n) {
  var r = e.pingCache;
  (r !== null && r.delete(t),
    (t = Ke()),
    (e.pingedLanes |= e.suspendedLanes & n),
    Oe === e &&
      (Me & n) === n &&
      (Ae === 4 || (Ae === 3 && (Me & 130023424) === Me && 500 > _e() - ju)
        ? $n(e, 0)
        : (Hu |= n)),
    tt(e, t));
}
function yg(e, t) {
  t === 0 &&
    (e.mode & 1
      ? ((t = ho), (ho <<= 1), !(ho & 130023424) && (ho = 4194304))
      : (t = 1));
  var n = Ke();
  ((e = Xt(e, t)), e !== null && (Xi(e, t, n), tt(e, n)));
}
function Kv(e) {
  var t = e.memoizedState,
    n = 0;
  (t !== null && (n = t.retryLane), yg(e, n));
}
function Vv(e, t) {
  var n = 0;
  switch (e.tag) {
    case 13:
      var r = e.stateNode,
        i = e.memoizedState;
      i !== null && (n = i.retryLane);
      break;
    case 19:
      r = e.stateNode;
      break;
    default:
      throw Error(P(314));
  }
  (r !== null && r.delete(t), yg(e, n));
}
var bg;
bg = function (e, t, n) {
  if (e !== null)
    if (e.memoizedProps !== t.pendingProps || Je.current) Xe = !0;
    else {
      if (!(e.lanes & n) && !(t.flags & 128)) return ((Xe = !1), Lv(e, t, n));
      Xe = !!(e.flags & 131072);
    }
  else ((Xe = !1), ye && t.flags & 1048576 && xh(t, cl, t.index));
  switch (((t.lanes = 0), t.tag)) {
    case 2:
      var r = t.type;
      (Wo(e, t), (e = t.pendingProps));
      var i = Mr(t, Be.current);
      (Tr(t, n), (i = Pu(null, t, r, e, i, n)));
      var o = zu();
      return (
        (t.flags |= 1),
        typeof i == "object" &&
        i !== null &&
        typeof i.render == "function" &&
        i.$$typeof === void 0
          ? ((t.tag = 1),
            (t.memoizedState = null),
            (t.updateQueue = null),
            et(r) ? ((o = !0), sl(t)) : (o = !1),
            (t.memoizedState =
              i.state !== null && i.state !== void 0 ? i.state : null),
            Ou(t),
            (i.updater = Bl),
            (t.stateNode = i),
            (i._reactInternals = t),
            Ss(t, r, e, n),
            (t = Ts(null, t, r, !0, o, n)))
          : ((t.tag = 0), ye && o && ku(t), We(null, t, i, n), (t = t.child)),
        t
      );
    case 16:
      r = t.elementType;
      e: {
        switch (
          (Wo(e, t),
          (e = t.pendingProps),
          (i = r._init),
          (r = i(r._payload)),
          (t.type = r),
          (i = t.tag = Yv(r)),
          (e = xt(r, e)),
          i)
        ) {
          case 0:
            t = Cs(null, t, r, e, n);
            break e;
          case 1:
            t = _d(null, t, r, e, n);
            break e;
          case 11:
            t = wd(null, t, r, e, n);
            break e;
          case 14:
            t = xd(null, t, r, xt(r.type, e), n);
            break e;
        }
        throw Error(P(306, r, ""));
      }
      return t;
    case 0:
      return (
        (r = t.type),
        (i = t.pendingProps),
        (i = t.elementType === r ? i : xt(r, i)),
        Cs(e, t, r, i, n)
      );
    case 1:
      return (
        (r = t.type),
        (i = t.pendingProps),
        (i = t.elementType === r ? i : xt(r, i)),
        _d(e, t, r, i, n)
      );
    case 3:
      e: {
        if ((tg(t), e === null)) throw Error(P(387));
        ((r = t.pendingProps),
          (o = t.memoizedState),
          (i = o.element),
          Th(e, t),
          pl(t, r, null, n));
        var l = t.memoizedState;
        if (((r = l.element), o.isDehydrated))
          if (
            ((o = {
              element: r,
              isDehydrated: !1,
              cache: l.cache,
              pendingSuspenseBoundaries: l.pendingSuspenseBoundaries,
              transitions: l.transitions,
            }),
            (t.updateQueue.baseState = o),
            (t.memoizedState = o),
            t.flags & 256)
          ) {
            ((i = zr(Error(P(423)), t)), (t = kd(e, t, r, n, i)));
            break e;
          } else if (r !== i) {
            ((i = zr(Error(P(424)), t)), (t = kd(e, t, r, n, i)));
            break e;
          } else
            for (
              lt = wn(t.stateNode.containerInfo.firstChild),
                at = t,
                ye = !0,
                kt = null,
                n = Nh(t, null, r, n),
                t.child = n;
              n;
            )
              ((n.flags = (n.flags & -3) | 4096), (n = n.sibling));
        else {
          if ((Lr(), r === i)) {
            t = Jt(e, t, n);
            break e;
          }
          We(e, t, r, n);
        }
        t = t.child;
      }
      return t;
    case 5:
      return (
        Ah(t),
        e === null && xs(t),
        (r = t.type),
        (i = t.pendingProps),
        (o = e !== null ? e.memoizedProps : null),
        (l = i.children),
        ys(r, i) ? (l = null) : o !== null && ys(r, o) && (t.flags |= 32),
        eg(e, t),
        We(e, t, l, n),
        t.child
      );
    case 6:
      return (e === null && xs(t), null);
    case 13:
      return ng(e, t, n);
    case 4:
      return (
        Iu(t, t.stateNode.containerInfo),
        (r = t.pendingProps),
        e === null ? (t.child = Dr(t, null, r, n)) : We(e, t, r, n),
        t.child
      );
    case 11:
      return (
        (r = t.type),
        (i = t.pendingProps),
        (i = t.elementType === r ? i : xt(r, i)),
        wd(e, t, r, i, n)
      );
    case 7:
      return (We(e, t, t.pendingProps, n), t.child);
    case 8:
      return (We(e, t, t.pendingProps.children, n), t.child);
    case 12:
      return (We(e, t, t.pendingProps.children, n), t.child);
    case 10:
      e: {
        if (
          ((r = t.type._context),
          (i = t.pendingProps),
          (o = t.memoizedProps),
          (l = i.value),
          fe(dl, r._currentValue),
          (r._currentValue = l),
          o !== null)
        )
          if (Tt(o.value, l)) {
            if (o.children === i.children && !Je.current) {
              t = Jt(e, t, n);
              break e;
            }
          } else
            for (o = t.child, o !== null && (o.return = t); o !== null;) {
              var a = o.dependencies;
              if (a !== null) {
                l = o.child;
                for (var s = a.firstContext; s !== null;) {
                  if (s.context === r) {
                    if (o.tag === 1) {
                      ((s = qt(-1, n & -n)), (s.tag = 2));
                      var u = o.updateQueue;
                      if (u !== null) {
                        u = u.shared;
                        var d = u.pending;
                        (d === null
                          ? (s.next = s)
                          : ((s.next = d.next), (d.next = s)),
                          (u.pending = s));
                      }
                    }
                    ((o.lanes |= n),
                      (s = o.alternate),
                      s !== null && (s.lanes |= n),
                      _s(o.return, n, t),
                      (a.lanes |= n));
                    break;
                  }
                  s = s.next;
                }
              } else if (o.tag === 10) l = o.type === t.type ? null : o.child;
              else if (o.tag === 18) {
                if (((l = o.return), l === null)) throw Error(P(341));
                ((l.lanes |= n),
                  (a = l.alternate),
                  a !== null && (a.lanes |= n),
                  _s(l, n, t),
                  (l = o.sibling));
              } else l = o.child;
              if (l !== null) l.return = o;
              else
                for (l = o; l !== null;) {
                  if (l === t) {
                    l = null;
                    break;
                  }
                  if (((o = l.sibling), o !== null)) {
                    ((o.return = l.return), (l = o));
                    break;
                  }
                  l = l.return;
                }
              o = l;
            }
        (We(e, t, i.children, n), (t = t.child));
      }
      return t;
    case 9:
      return (
        (i = t.type),
        (r = t.pendingProps.children),
        Tr(t, n),
        (i = yt(i)),
        (r = r(i)),
        (t.flags |= 1),
        We(e, t, r, n),
        t.child
      );
    case 14:
      return (
        (r = t.type),
        (i = xt(r, t.pendingProps)),
        (i = xt(r.type, i)),
        xd(e, t, r, i, n)
      );
    case 15:
      return Xh(e, t, t.type, t.pendingProps, n);
    case 17:
      return (
        (r = t.type),
        (i = t.pendingProps),
        (i = t.elementType === r ? i : xt(r, i)),
        Wo(e, t),
        (t.tag = 1),
        et(r) ? ((e = !0), sl(t)) : (e = !1),
        Tr(t, n),
        Yh(t, r, i),
        Ss(t, r, i, n),
        Ts(null, t, r, !0, e, n)
      );
    case 19:
      return rg(e, t, n);
    case 22:
      return Jh(e, t, n);
  }
  throw Error(P(156, t.tag));
};
function vg(e, t) {
  return Kp(e, t);
}
function qv(e, t, n, r) {
  ((this.tag = e),
    (this.key = n),
    (this.sibling =
      this.child =
      this.return =
      this.stateNode =
      this.type =
      this.elementType =
        null),
    (this.index = 0),
    (this.ref = null),
    (this.pendingProps = t),
    (this.dependencies =
      this.memoizedState =
      this.updateQueue =
      this.memoizedProps =
        null),
    (this.mode = r),
    (this.subtreeFlags = this.flags = 0),
    (this.deletions = null),
    (this.childLanes = this.lanes = 0),
    (this.alternate = null));
}
function gt(e, t, n, r) {
  return new qv(e, t, n, r);
}
function Vu(e) {
  return ((e = e.prototype), !(!e || !e.isReactComponent));
}
function Yv(e) {
  if (typeof e == "function") return Vu(e) ? 1 : 0;
  if (e != null) {
    if (((e = e.$$typeof), e === fu)) return 11;
    if (e === pu) return 14;
  }
  return 2;
}
function Sn(e, t) {
  var n = e.alternate;
  return (
    n === null
      ? ((n = gt(e.tag, t, e.key, e.mode)),
        (n.elementType = e.elementType),
        (n.type = e.type),
        (n.stateNode = e.stateNode),
        (n.alternate = e),
        (e.alternate = n))
      : ((n.pendingProps = t),
        (n.type = e.type),
        (n.flags = 0),
        (n.subtreeFlags = 0),
        (n.deletions = null)),
    (n.flags = e.flags & 14680064),
    (n.childLanes = e.childLanes),
    (n.lanes = e.lanes),
    (n.child = e.child),
    (n.memoizedProps = e.memoizedProps),
    (n.memoizedState = e.memoizedState),
    (n.updateQueue = e.updateQueue),
    (t = e.dependencies),
    (n.dependencies =
      t === null ? null : { lanes: t.lanes, firstContext: t.firstContext }),
    (n.sibling = e.sibling),
    (n.index = e.index),
    (n.ref = e.ref),
    n
  );
}
function Vo(e, t, n, r, i, o) {
  var l = 2;
  if (((r = e), typeof e == "function")) Vu(e) && (l = 1);
  else if (typeof e == "string") l = 5;
  else
    e: switch (e) {
      case pr:
        return Hn(n.children, i, o, t);
      case du:
        ((l = 8), (i |= 8));
        break;
      case Ya:
        return (
          (e = gt(12, n, t, i | 2)),
          (e.elementType = Ya),
          (e.lanes = o),
          e
        );
      case Qa:
        return ((e = gt(13, n, t, i)), (e.elementType = Qa), (e.lanes = o), e);
      case Za:
        return ((e = gt(19, n, t, i)), (e.elementType = Za), (e.lanes = o), e);
      case Ap:
        return Hl(n, i, o, t);
      default:
        if (typeof e == "object" && e !== null)
          switch (e.$$typeof) {
            case Cp:
              l = 10;
              break e;
            case Tp:
              l = 9;
              break e;
            case fu:
              l = 11;
              break e;
            case pu:
              l = 14;
              break e;
            case cn:
              ((l = 16), (r = null));
              break e;
          }
        throw Error(P(130, e == null ? e : typeof e, ""));
    }
  return (
    (t = gt(l, n, t, i)),
    (t.elementType = e),
    (t.type = r),
    (t.lanes = o),
    t
  );
}
function Hn(e, t, n, r) {
  return ((e = gt(7, e, r, t)), (e.lanes = n), e);
}
function Hl(e, t, n, r) {
  return (
    (e = gt(22, e, r, t)),
    (e.elementType = Ap),
    (e.lanes = n),
    (e.stateNode = { isHidden: !1 }),
    e
  );
}
function Sa(e, t, n) {
  return ((e = gt(6, e, null, t)), (e.lanes = n), e);
}
function Na(e, t, n) {
  return (
    (t = gt(4, e.children !== null ? e.children : [], e.key, t)),
    (t.lanes = n),
    (t.stateNode = {
      containerInfo: e.containerInfo,
      pendingChildren: null,
      implementation: e.implementation,
    }),
    t
  );
}
function Qv(e, t, n, r, i) {
  ((this.tag = t),
    (this.containerInfo = e),
    (this.finishedWork =
      this.pingCache =
      this.current =
      this.pendingChildren =
        null),
    (this.timeoutHandle = -1),
    (this.callbackNode = this.pendingContext = this.context = null),
    (this.callbackPriority = 0),
    (this.eventTimes = la(0)),
    (this.expirationTimes = la(-1)),
    (this.entangledLanes =
      this.finishedLanes =
      this.mutableReadLanes =
      this.expiredLanes =
      this.pingedLanes =
      this.suspendedLanes =
      this.pendingLanes =
        0),
    (this.entanglements = la(0)),
    (this.identifierPrefix = r),
    (this.onRecoverableError = i),
    (this.mutableSourceEagerHydrationData = null));
}
function qu(e, t, n, r, i, o, l, a, s) {
  return (
    (e = new Qv(e, t, n, a, s)),
    t === 1 ? ((t = 1), o === !0 && (t |= 8)) : (t = 0),
    (o = gt(3, null, null, t)),
    (e.current = o),
    (o.stateNode = e),
    (o.memoizedState = {
      element: r,
      isDehydrated: n,
      cache: null,
      transitions: null,
      pendingSuspenseBoundaries: null,
    }),
    Ou(o),
    e
  );
}
function Zv(e, t, n) {
  var r = 3 < arguments.length && arguments[3] !== void 0 ? arguments[3] : null;
  return {
    $$typeof: fr,
    key: r == null ? null : "" + r,
    children: e,
    containerInfo: t,
    implementation: n,
  };
}
function Eg(e) {
  if (!e) return Cn;
  e = e._reactInternals;
  e: {
    if (Jn(e) !== e || e.tag !== 1) throw Error(P(170));
    var t = e;
    do {
      switch (t.tag) {
        case 3:
          t = t.stateNode.context;
          break e;
        case 1:
          if (et(t.type)) {
            t = t.stateNode.__reactInternalMemoizedMergedChildContext;
            break e;
          }
      }
      t = t.return;
    } while (t !== null);
    throw Error(P(171));
  }
  if (e.tag === 1) {
    var n = e.type;
    if (et(n)) return Eh(e, n, t);
  }
  return t;
}
function wg(e, t, n, r, i, o, l, a, s) {
  return (
    (e = qu(n, r, !0, e, i, o, l, a, s)),
    (e.context = Eg(null)),
    (n = e.current),
    (r = Ke()),
    (i = kn(n)),
    (o = qt(r, i)),
    (o.callback = t ?? null),
    xn(n, o, i),
    (e.current.lanes = i),
    Xi(e, i, r),
    tt(e, r),
    e
  );
}
function jl(e, t, n, r) {
  var i = t.current,
    o = Ke(),
    l = kn(i);
  return (
    (n = Eg(n)),
    t.context === null ? (t.context = n) : (t.pendingContext = n),
    (t = qt(o, l)),
    (t.payload = { element: e }),
    (r = r === void 0 ? null : r),
    r !== null && (t.callback = r),
    (e = xn(i, t, l)),
    e !== null && (Nt(e, i, l, o), $o(e, i, l)),
    l
  );
}
function wl(e) {
  if (((e = e.current), !e.child)) return null;
  switch (e.child.tag) {
    case 5:
      return e.child.stateNode;
    default:
      return e.child.stateNode;
  }
}
function Ld(e, t) {
  if (((e = e.memoizedState), e !== null && e.dehydrated !== null)) {
    var n = e.retryLane;
    e.retryLane = n !== 0 && n < t ? n : t;
  }
}
function Yu(e, t) {
  (Ld(e, t), (e = e.alternate) && Ld(e, t));
}
function Xv() {
  return null;
}
var xg =
  typeof reportError == "function"
    ? reportError
    : function (e) {
        console.error(e);
      };
function Qu(e) {
  this._internalRoot = e;
}
Wl.prototype.render = Qu.prototype.render = function (e) {
  var t = this._internalRoot;
  if (t === null) throw Error(P(409));
  jl(e, t, null, null);
};
Wl.prototype.unmount = Qu.prototype.unmount = function () {
  var e = this._internalRoot;
  if (e !== null) {
    this._internalRoot = null;
    var t = e.containerInfo;
    (Qn(function () {
      jl(null, e, null, null);
    }),
      (t[Zt] = null));
  }
};
function Wl(e) {
  this._internalRoot = e;
}
Wl.prototype.unstable_scheduleHydration = function (e) {
  if (e) {
    var t = Jp();
    e = { blockedOn: null, target: e, priority: t };
    for (var n = 0; n < fn.length && t !== 0 && t < fn[n].priority; n++);
    (fn.splice(n, 0, e), n === 0 && th(e));
  }
};
function Zu(e) {
  return !(!e || (e.nodeType !== 1 && e.nodeType !== 9 && e.nodeType !== 11));
}
function Gl(e) {
  return !(
    !e ||
    (e.nodeType !== 1 &&
      e.nodeType !== 9 &&
      e.nodeType !== 11 &&
      (e.nodeType !== 8 || e.nodeValue !== " react-mount-point-unstable "))
  );
}
function Dd() {}
function Jv(e, t, n, r, i) {
  if (i) {
    if (typeof r == "function") {
      var o = r;
      r = function () {
        var u = wl(l);
        o.call(u);
      };
    }
    var l = wg(t, r, e, 0, null, !1, !1, "", Dd);
    return (
      (e._reactRootContainer = l),
      (e[Zt] = l.current),
      Pi(e.nodeType === 8 ? e.parentNode : e),
      Qn(),
      l
    );
  }
  for (; (i = e.lastChild);) e.removeChild(i);
  if (typeof r == "function") {
    var a = r;
    r = function () {
      var u = wl(s);
      a.call(u);
    };
  }
  var s = qu(e, 0, !1, null, null, !1, !1, "", Dd);
  return (
    (e._reactRootContainer = s),
    (e[Zt] = s.current),
    Pi(e.nodeType === 8 ? e.parentNode : e),
    Qn(function () {
      jl(t, s, n, r);
    }),
    s
  );
}
function Kl(e, t, n, r, i) {
  var o = n._reactRootContainer;
  if (o) {
    var l = o;
    if (typeof i == "function") {
      var a = i;
      i = function () {
        var s = wl(l);
        a.call(s);
      };
    }
    jl(t, l, e, i);
  } else l = Jv(n, t, e, i, r);
  return wl(l);
}
Zp = function (e) {
  switch (e.tag) {
    case 3:
      var t = e.stateNode;
      if (t.current.memoizedState.isDehydrated) {
        var n = hi(t.pendingLanes);
        n !== 0 &&
          (mu(t, n | 1), tt(t, _e()), !(ie & 6) && ((Fr = _e() + 500), Rn()));
      }
      break;
    case 13:
      (Qn(function () {
        var r = Xt(e, 1);
        if (r !== null) {
          var i = Ke();
          Nt(r, e, 1, i);
        }
      }),
        Yu(e, 1));
  }
};
yu = function (e) {
  if (e.tag === 13) {
    var t = Xt(e, 134217728);
    if (t !== null) {
      var n = Ke();
      Nt(t, e, 134217728, n);
    }
    Yu(e, 134217728);
  }
};
Xp = function (e) {
  if (e.tag === 13) {
    var t = kn(e),
      n = Xt(e, t);
    if (n !== null) {
      var r = Ke();
      Nt(n, e, t, r);
    }
    Yu(e, t);
  }
};
Jp = function () {
  return ae;
};
eh = function (e, t) {
  var n = ae;
  try {
    return ((ae = e), t());
  } finally {
    ae = n;
  }
};
as = function (e, t, n) {
  switch (t) {
    case "input":
      if ((es(e, n), (t = n.name), n.type === "radio" && t != null)) {
        for (n = e; n.parentNode;) n = n.parentNode;
        for (
          n = n.querySelectorAll(
            "input[name=" + JSON.stringify("" + t) + '][type="radio"]',
          ),
            t = 0;
          t < n.length;
          t++
        ) {
          var r = n[t];
          if (r !== e && r.form === e.form) {
            var i = Pl(r);
            if (!i) throw Error(P(90));
            (Op(r), es(r, i));
          }
        }
      }
      break;
    case "textarea":
      Mp(e, n);
      break;
    case "select":
      ((t = n.value), t != null && kr(e, !!n.multiple, t, !1));
  }
};
Up = Wu;
$p = Qn;
var eE = { usingClientEntryPoint: !1, Events: [eo, yr, Pl, Fp, Bp, Wu] },
  li = {
    findFiberByHostInstance: Fn,
    bundleType: 0,
    version: "18.3.1",
    rendererPackageName: "react-dom",
  },
  tE = {
    bundleType: li.bundleType,
    version: li.version,
    rendererPackageName: li.rendererPackageName,
    rendererConfig: li.rendererConfig,
    overrideHookState: null,
    overrideHookStateDeletePath: null,
    overrideHookStateRenamePath: null,
    overrideProps: null,
    overridePropsDeletePath: null,
    overridePropsRenamePath: null,
    setErrorHandler: null,
    setSuspenseHandler: null,
    scheduleUpdate: null,
    currentDispatcherRef: en.ReactCurrentDispatcher,
    findHostInstanceByFiber: function (e) {
      return ((e = Wp(e)), e === null ? null : e.stateNode);
    },
    findFiberByHostInstance: li.findFiberByHostInstance || Xv,
    findHostInstancesForRefresh: null,
    scheduleRefresh: null,
    scheduleRoot: null,
    setRefreshHandler: null,
    getCurrentFiber: null,
    reconcilerVersion: "18.3.1-next-f1338f8080-20240426",
  };
if (typeof __REACT_DEVTOOLS_GLOBAL_HOOK__ < "u") {
  var So = __REACT_DEVTOOLS_GLOBAL_HOOK__;
  if (!So.isDisabled && So.supportsFiber)
    try {
      ((Il = So.inject(tE)), (zt = So));
    } catch {}
}
ct.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED = eE;
ct.createPortal = function (e, t) {
  var n = 2 < arguments.length && arguments[2] !== void 0 ? arguments[2] : null;
  if (!Zu(t)) throw Error(P(200));
  return Zv(e, t, null, n);
};
ct.createRoot = function (e, t) {
  if (!Zu(e)) throw Error(P(299));
  var n = !1,
    r = "",
    i = xg;
  return (
    t != null &&
      (t.unstable_strictMode === !0 && (n = !0),
      t.identifierPrefix !== void 0 && (r = t.identifierPrefix),
      t.onRecoverableError !== void 0 && (i = t.onRecoverableError)),
    (t = qu(e, 1, !1, null, null, n, !1, r, i)),
    (e[Zt] = t.current),
    Pi(e.nodeType === 8 ? e.parentNode : e),
    new Qu(t)
  );
};
ct.findDOMNode = function (e) {
  if (e == null) return null;
  if (e.nodeType === 1) return e;
  var t = e._reactInternals;
  if (t === void 0)
    throw typeof e.render == "function"
      ? Error(P(188))
      : ((e = Object.keys(e).join(",")), Error(P(268, e)));
  return ((e = Wp(t)), (e = e === null ? null : e.stateNode), e);
};
ct.flushSync = function (e) {
  return Qn(e);
};
ct.hydrate = function (e, t, n) {
  if (!Gl(t)) throw Error(P(200));
  return Kl(null, e, t, !0, n);
};
ct.hydrateRoot = function (e, t, n) {
  if (!Zu(e)) throw Error(P(405));
  var r = (n != null && n.hydratedSources) || null,
    i = !1,
    o = "",
    l = xg;
  if (
    (n != null &&
      (n.unstable_strictMode === !0 && (i = !0),
      n.identifierPrefix !== void 0 && (o = n.identifierPrefix),
      n.onRecoverableError !== void 0 && (l = n.onRecoverableError)),
    (t = wg(t, null, e, 1, n ?? null, i, !1, o, l)),
    (e[Zt] = t.current),
    Pi(e),
    r)
  )
    for (e = 0; e < r.length; e++)
      ((n = r[e]),
        (i = n._getVersion),
        (i = i(n._source)),
        t.mutableSourceEagerHydrationData == null
          ? (t.mutableSourceEagerHydrationData = [n, i])
          : t.mutableSourceEagerHydrationData.push(n, i));
  return new Wl(t);
};
ct.render = function (e, t, n) {
  if (!Gl(t)) throw Error(P(200));
  return Kl(null, e, t, !1, n);
};
ct.unmountComponentAtNode = function (e) {
  if (!Gl(e)) throw Error(P(40));
  return e._reactRootContainer
    ? (Qn(function () {
        Kl(null, null, e, !1, function () {
          ((e._reactRootContainer = null), (e[Zt] = null));
        });
      }),
      !0)
    : !1;
};
ct.unstable_batchedUpdates = Wu;
ct.unstable_renderSubtreeIntoContainer = function (e, t, n, r) {
  if (!Gl(n)) throw Error(P(200));
  if (e == null || e._reactInternals === void 0) throw Error(P(38));
  return Kl(e, t, n, !1, r);
};
ct.version = "18.3.1-next-f1338f8080-20240426";
function _g() {
  if (!(
    typeof __REACT_DEVTOOLS_GLOBAL_HOOK__ > "u" ||
    typeof __REACT_DEVTOOLS_GLOBAL_HOOK__.checkDCE != "function"
  ))
    try {
      __REACT_DEVTOOLS_GLOBAL_HOOK__.checkDCE(_g);
    } catch (e) {
      console.error(e);
    }
}
(_g(), (_p.exports = ct));
var nE = _p.exports,
  Pd = nE;
((Va.createRoot = Pd.createRoot), (Va.hydrateRoot = Pd.hydrateRoot));
/**
 * @remix-run/router v1.23.3
 *
 * Copyright (c) Remix Software Inc.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE.md file in the root directory of this source tree.
 *
 * @license MIT
 */ function Gi() {
  return (
    (Gi = Object.assign
      ? Object.assign.bind()
      : function (e) {
          for (var t = 1; t < arguments.length; t++) {
            var n = arguments[t];
            for (var r in n) ({}).hasOwnProperty.call(n, r) && (e[r] = n[r]);
          }
          return e;
        }),
    Gi.apply(null, arguments)
  );
}
var mn;
(function (e) {
  ((e.Pop = "POP"), (e.Push = "PUSH"), (e.Replace = "REPLACE"));
})(mn || (mn = {}));
const zd = "popstate";
function rE(e) {
  e === void 0 && (e = {});
  function t(r, i) {
    let { pathname: o, search: l, hash: a } = r.location;
    return Us(
      "",
      { pathname: o, search: l, hash: a },
      (i.state && i.state.usr) || null,
      (i.state && i.state.key) || "default",
    );
  }
  function n(r, i) {
    return typeof i == "string" ? i : kg(i);
  }
  return oE(t, n, null, e);
}
function Ce(e, t) {
  if (e === !1 || e === null || typeof e > "u") throw new Error(t);
}
function Xu(e, t) {
  if (!e) {
    typeof console < "u" && console.warn(t);
    try {
      throw new Error(t);
    } catch {}
  }
}
function iE() {
  return Math.random().toString(36).substr(2, 8);
}
function Fd(e, t) {
  return { usr: e.state, key: e.key, idx: t };
}
function Us(e, t, n, r) {
  return (
    n === void 0 && (n = null),
    Gi(
      { pathname: typeof e == "string" ? e : e.pathname, search: "", hash: "" },
      typeof t == "string" ? Wr(t) : t,
      { state: n, key: (t && t.key) || r || iE() },
    )
  );
}
function kg(e) {
  let { pathname: t = "/", search: n = "", hash: r = "" } = e;
  return (
    n && n !== "?" && (t += n.charAt(0) === "?" ? n : "?" + n),
    r && r !== "#" && (t += r.charAt(0) === "#" ? r : "#" + r),
    t
  );
}
function Wr(e) {
  let t = {};
  if (e) {
    let n = e.indexOf("#");
    n >= 0 && ((t.hash = e.substr(n)), (e = e.substr(0, n)));
    let r = e.indexOf("?");
    (r >= 0 && ((t.search = e.substr(r)), (e = e.substr(0, r))),
      e && (t.pathname = e));
  }
  return t;
}
function oE(e, t, n, r) {
  r === void 0 && (r = {});
  let { window: i = document.defaultView, v5Compat: o = !1 } = r,
    l = i.history,
    a = mn.Pop,
    s = null,
    u = d();
  u == null && ((u = 0), l.replaceState(Gi({}, l.state, { idx: u }), ""));
  function d() {
    return (l.state || { idx: null }).idx;
  }
  function c() {
    a = mn.Pop;
    let E = d(),
      h = E == null ? null : E - u;
    ((u = E), s && s({ action: a, location: y.location, delta: h }));
  }
  function f(E, h) {
    a = mn.Push;
    let m = Us(y.location, E, h);
    u = d() + 1;
    let b = Fd(m, u),
      _ = y.createHref(m);
    try {
      l.pushState(b, "", _);
    } catch (N) {
      if (N instanceof DOMException && N.name === "DataCloneError") throw N;
      i.location.assign(_);
    }
    o && s && s({ action: a, location: y.location, delta: 1 });
  }
  function p(E, h) {
    a = mn.Replace;
    let m = Us(y.location, E, h);
    u = d();
    let b = Fd(m, u),
      _ = y.createHref(m);
    (l.replaceState(b, "", _),
      o && s && s({ action: a, location: y.location, delta: 0 }));
  }
  function g(E) {
    let h = i.location.origin !== "null" ? i.location.origin : i.location.href,
      m = typeof E == "string" ? E : kg(E);
    return (
      (m = m.replace(/ $/, "%20")),
      Ce(
        h,
        "No window.location.(origin|href) available to create URL for href: " +
          m,
      ),
      new URL(m, h)
    );
  }
  let y = {
    get action() {
      return a;
    },
    get location() {
      return e(i, l);
    },
    listen(E) {
      if (s) throw new Error("A history only accepts one active listener");
      return (
        i.addEventListener(zd, c),
        (s = E),
        () => {
          (i.removeEventListener(zd, c), (s = null));
        }
      );
    },
    createHref(E) {
      return t(i, E);
    },
    createURL: g,
    encodeLocation(E) {
      let h = g(E);
      return { pathname: h.pathname, search: h.search, hash: h.hash };
    },
    push: f,
    replace: p,
    go(E) {
      return l.go(E);
    },
  };
  return y;
}
var Bd;
(function (e) {
  ((e.data = "data"),
    (e.deferred = "deferred"),
    (e.redirect = "redirect"),
    (e.error = "error"));
})(Bd || (Bd = {}));
function lE(e, t, n) {
  return (n === void 0 && (n = "/"), aE(e, t, n));
}
function aE(e, t, n, r) {
  let i = typeof t == "string" ? Wr(t) : t,
    o = Cg(i.pathname || "/", n);
  if (o == null) return null;
  let l = Sg(e);
  sE(l);
  let a = null,
    s = EE(o);
  for (let u = 0; a == null && u < l.length; ++u) a = yE(l[u], s);
  return a;
}
function Sg(e, t, n, r) {
  (t === void 0 && (t = []),
    n === void 0 && (n = []),
    r === void 0 && (r = ""));
  let i = (o, l, a) => {
    let s = {
      relativePath: a === void 0 ? o.path || "" : a,
      caseSensitive: o.caseSensitive === !0,
      childrenIndex: l,
      route: o,
    };
    s.relativePath.startsWith("/") &&
      (Ce(
        s.relativePath.startsWith(r),
        'Absolute route path "' +
          s.relativePath +
          '" nested under path ' +
          ('"' + r + '" is not valid. An absolute child route path ') +
          "must start with the combined path of all its parent routes.",
      ),
      (s.relativePath = s.relativePath.slice(r.length)));
    let u = jn([r, s.relativePath]),
      d = n.concat(s);
    (o.children &&
      o.children.length > 0 &&
      (Ce(
        o.index !== !0,
        "Index routes must not have child routes. Please remove " +
          ('all child routes from route path "' + u + '".'),
      ),
      Sg(o.children, t, d, u)),
      !(o.path == null && !o.index) &&
        t.push({ path: u, score: gE(u, o.index), routesMeta: d }));
  };
  return (
    e.forEach((o, l) => {
      var a;
      if (o.path === "" || !((a = o.path) != null && a.includes("?"))) i(o, l);
      else for (let s of Ng(o.path)) i(o, l, s);
    }),
    t
  );
}
function Ng(e) {
  let t = e.split("/");
  if (t.length === 0) return [];
  let [n, ...r] = t,
    i = n.endsWith("?"),
    o = n.replace(/\?$/, "");
  if (r.length === 0) return i ? [o, ""] : [o];
  let l = Ng(r.join("/")),
    a = [];
  return (
    a.push(...l.map((s) => (s === "" ? o : [o, s].join("/")))),
    i && a.push(...l),
    a.map((s) => (e.startsWith("/") && s === "" ? "/" : s))
  );
}
function sE(e) {
  e.sort((t, n) =>
    t.score !== n.score
      ? n.score - t.score
      : mE(
          t.routesMeta.map((r) => r.childrenIndex),
          n.routesMeta.map((r) => r.childrenIndex),
        ),
  );
}
const uE = /^:[\w-]+$/,
  cE = 3,
  dE = 2,
  fE = 1,
  pE = 10,
  hE = -2,
  Ud = (e) => e === "*";
function gE(e, t) {
  let n = e.split("/"),
    r = n.length;
  return (
    n.some(Ud) && (r += hE),
    t && (r += dE),
    n
      .filter((i) => !Ud(i))
      .reduce((i, o) => i + (uE.test(o) ? cE : o === "" ? fE : pE), r)
  );
}
function mE(e, t) {
  return e.length === t.length && e.slice(0, -1).every((r, i) => r === t[i])
    ? e[e.length - 1] - t[t.length - 1]
    : 0;
}
function yE(e, t, n) {
  let { routesMeta: r } = e,
    i = {},
    o = "/",
    l = [];
  for (let a = 0; a < r.length; ++a) {
    let s = r[a],
      u = a === r.length - 1,
      d = o === "/" ? t : t.slice(o.length) || "/",
      c = bE(
        { path: s.relativePath, caseSensitive: s.caseSensitive, end: u },
        d,
      ),
      f = s.route;
    if (!c) return null;
    (Object.assign(i, c.params),
      l.push({
        params: i,
        pathname: jn([o, c.pathname]),
        pathnameBase: SE(jn([o, c.pathnameBase])),
        route: f,
      }),
      c.pathnameBase !== "/" && (o = jn([o, c.pathnameBase])));
  }
  return l;
}
function bE(e, t) {
  typeof e == "string" && (e = { path: e, caseSensitive: !1, end: !0 });
  let [n, r] = vE(e.path, e.caseSensitive, e.end),
    i = t.match(n);
  if (!i) return null;
  let o = i[0],
    l = o.replace(/(.)\/+$/, "$1"),
    a = i.slice(1);
  return {
    params: r.reduce((u, d, c) => {
      let { paramName: f, isOptional: p } = d;
      if (f === "*") {
        let y = a[c] || "";
        l = o.slice(0, o.length - y.length).replace(/(.)\/+$/, "$1");
      }
      const g = a[c];
      return (
        p && !g ? (u[f] = void 0) : (u[f] = (g || "").replace(/%2F/g, "/")),
        u
      );
    }, {}),
    pathname: o,
    pathnameBase: l,
    pattern: e,
  };
}
function vE(e, t, n) {
  (t === void 0 && (t = !1),
    n === void 0 && (n = !0),
    Xu(
      e === "*" || !e.endsWith("*") || e.endsWith("/*"),
      'Route path "' +
        e +
        '" will be treated as if it were ' +
        ('"' + e.replace(/\*$/, "/*") + '" because the `*` character must ') +
        "always follow a `/` in the pattern. To get rid of this warning, " +
        ('please change the route path to "' + e.replace(/\*$/, "/*") + '".'),
    ));
  let r = [],
    i =
      "^" +
      e
        .replace(/\/*\*?$/, "")
        .replace(/^\/*/, "/")
        .replace(/[\\.*+^${}|()[\]]/g, "\\$&")
        .replace(
          /\/:([\w-]+)(\?)?/g,
          (l, a, s) => (
            r.push({ paramName: a, isOptional: s != null }),
            s ? "/?([^\\/]+)?" : "/([^\\/]+)"
          ),
        );
  return (
    e.endsWith("*")
      ? (r.push({ paramName: "*" }),
        (i += e === "*" || e === "/*" ? "(.*)$" : "(?:\\/(.+)|\\/*)$"))
      : n
        ? (i += "\\/*$")
        : e !== "" && e !== "/" && (i += "(?:(?=\\/|$))"),
    [new RegExp(i, t ? void 0 : "i"), r]
  );
}
function EE(e) {
  try {
    return e
      .split("/")
      .map((t) => decodeURIComponent(t).replace(/\//g, "%2F"))
      .join("/");
  } catch (t) {
    return (
      Xu(
        !1,
        'The URL path "' +
          e +
          '" could not be decoded because it is is a malformed URL segment. This is probably due to a bad percent ' +
          ("encoding (" + t + ")."),
      ),
      e
    );
  }
}
function Cg(e, t) {
  if (t === "/") return e;
  if (!e.toLowerCase().startsWith(t.toLowerCase())) return null;
  let n = t.endsWith("/") ? t.length - 1 : t.length,
    r = e.charAt(n);
  return r && r !== "/" ? null : e.slice(n) || "/";
}
const wE = /^(?:[a-z][a-z0-9+.-]*:|\/\/)/i,
  xE = (e) => wE.test(e);
function _E(e, t) {
  t === void 0 && (t = "/");
  let {
      pathname: n,
      search: r = "",
      hash: i = "",
    } = typeof e == "string" ? Wr(e) : e,
    o;
  if (n)
    if (xE(n)) o = n;
    else {
      if (n.includes("//")) {
        let l = n;
        ((n = Rg(n)),
          Xu(
            !1,
            "Pathnames cannot have embedded double slashes - normalizing " +
              (l + " -> " + n),
          ));
      }
      n.startsWith("/") ? (o = $d(n.substring(1), "/")) : (o = $d(n, t));
    }
  else o = t;
  return { pathname: o, search: NE(r), hash: CE(i) };
}
function $d(e, t) {
  let n = t.replace(/\/+$/, "").split("/");
  return (
    e.split("/").forEach((i) => {
      i === ".." ? n.length > 1 && n.pop() : i !== "." && n.push(i);
    }),
    n.length > 1 ? n.join("/") : "/"
  );
}
function Ca(e, t, n, r) {
  return (
    "Cannot include a '" +
    e +
    "' character in a manually specified " +
    ("`to." +
      t +
      "` field [" +
      JSON.stringify(r) +
      "].  Please separate it out to the ") +
    ("`to." + n + "` field. Alternatively you may provide the full path as ") +
    'a string in <Link to="..."> and the router will parse it for you.'
  );
}
function kE(e) {
  return e.filter(
    (t, n) => n === 0 || (t.route.path && t.route.path.length > 0),
  );
}
function Tg(e, t) {
  let n = kE(e);
  return t
    ? n.map((r, i) => (i === n.length - 1 ? r.pathname : r.pathnameBase))
    : n.map((r) => r.pathnameBase);
}
function Ag(e, t, n, r) {
  r === void 0 && (r = !1);
  let i;
  typeof e == "string"
    ? (i = Wr(e))
    : ((i = Gi({}, e)),
      Ce(
        !i.pathname || !i.pathname.includes("?"),
        Ca("?", "pathname", "search", i),
      ),
      Ce(
        !i.pathname || !i.pathname.includes("#"),
        Ca("#", "pathname", "hash", i),
      ),
      Ce(!i.search || !i.search.includes("#"), Ca("#", "search", "hash", i)));
  let o = e === "" || i.pathname === "",
    l = o ? "/" : i.pathname,
    a;
  if (l == null) a = n;
  else {
    let c = t.length - 1;
    if (!r && l.startsWith("..")) {
      let f = l.split("/");
      for (; f[0] === "..";) (f.shift(), (c -= 1));
      i.pathname = f.join("/");
    }
    a = c >= 0 ? t[c] : "/";
  }
  let s = _E(i, a),
    u = l && l !== "/" && l.endsWith("/"),
    d = (o || l === ".") && n.endsWith("/");
  return (!s.pathname.endsWith("/") && (u || d) && (s.pathname += "/"), s);
}
const Rg = (e) => e.replace(/\/\/+/g, "/"),
  jn = (e) => Rg(e.join("/")),
  SE = (e) => e.replace(/\/+$/, "").replace(/^\/*/, "/"),
  NE = (e) => (!e || e === "?" ? "" : e.startsWith("?") ? e : "?" + e),
  CE = (e) => (!e || e === "#" ? "" : e.startsWith("#") ? e : "#" + e);
function TE(e) {
  return (
    e != null &&
    typeof e.status == "number" &&
    typeof e.statusText == "string" &&
    typeof e.internal == "boolean" &&
    "data" in e
  );
}
const Og = ["post", "put", "patch", "delete"];
new Set(Og);
const AE = ["get", ...Og];
new Set(AE);
/**
 * React Router v6.30.4
 *
 * Copyright (c) Remix Software Inc.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE.md file in the root directory of this source tree.
 *
 * @license MIT
 */ function Ki() {
  return (
    (Ki = Object.assign
      ? Object.assign.bind()
      : function (e) {
          for (var t = 1; t < arguments.length; t++) {
            var n = arguments[t];
            for (var r in n) ({}).hasOwnProperty.call(n, r) && (e[r] = n[r]);
          }
          return e;
        }),
    Ki.apply(null, arguments)
  );
}
const Ju = D.createContext(null),
  RE = D.createContext(null),
  no = D.createContext(null),
  Vl = D.createContext(null),
  er = D.createContext({ outlet: null, matches: [], isDataRoute: !1 }),
  Ig = D.createContext(null);
function ro() {
  return D.useContext(Vl) != null;
}
function ec() {
  return (ro() || Ce(!1), D.useContext(Vl).location);
}
function Mg(e) {
  D.useContext(no).static || D.useLayoutEffect(e);
}
function tc() {
  let { isDataRoute: e } = D.useContext(er);
  return e ? jE() : OE();
}
function OE() {
  ro() || Ce(!1);
  let e = D.useContext(Ju),
    { basename: t, future: n, navigator: r } = D.useContext(no),
    { matches: i } = D.useContext(er),
    { pathname: o } = ec(),
    l = JSON.stringify(Tg(i, n.v7_relativeSplatPath)),
    a = D.useRef(!1);
  return (
    Mg(() => {
      a.current = !0;
    }),
    D.useCallback(
      function (u, d) {
        if ((d === void 0 && (d = {}), !a.current)) return;
        if (typeof u == "number") {
          r.go(u);
          return;
        }
        let c = Ag(u, JSON.parse(l), o, d.relative === "path");
        (e == null &&
          t !== "/" &&
          (c.pathname = c.pathname === "/" ? t : jn([t, c.pathname])),
          (d.replace ? r.replace : r.push)(c, d.state, d));
      },
      [t, r, l, o, e],
    )
  );
}
function IE(e, t) {
  return ME(e, t);
}
function ME(e, t, n, r) {
  ro() || Ce(!1);
  let { navigator: i } = D.useContext(no),
    { matches: o } = D.useContext(er),
    l = o[o.length - 1],
    a = l ? l.params : {};
  l && l.pathname;
  let s = l ? l.pathnameBase : "/";
  l && l.route;
  let u = ec(),
    d;
  if (t) {
    var c;
    let E = typeof t == "string" ? Wr(t) : t;
    (s === "/" || ((c = E.pathname) != null && c.startsWith(s)) || Ce(!1),
      (d = E));
  } else d = u;
  let f = d.pathname || "/",
    p = f;
  if (s !== "/") {
    let E = s.replace(/^\//, "").split("/");
    p = "/" + f.replace(/^\//, "").split("/").slice(E.length).join("/");
  }
  let g = lE(e, { pathname: p }),
    y = FE(
      g &&
        g.map((E) =>
          Object.assign({}, E, {
            params: Object.assign({}, a, E.params),
            pathname: jn([
              s,
              i.encodeLocation
                ? i.encodeLocation(E.pathname).pathname
                : E.pathname,
            ]),
            pathnameBase:
              E.pathnameBase === "/"
                ? s
                : jn([
                    s,
                    i.encodeLocation
                      ? i.encodeLocation(E.pathnameBase).pathname
                      : E.pathnameBase,
                  ]),
          }),
        ),
      o,
      n,
      r,
    );
  return t && y
    ? D.createElement(
        Vl.Provider,
        {
          value: {
            location: Ki(
              {
                pathname: "/",
                search: "",
                hash: "",
                state: null,
                key: "default",
              },
              d,
            ),
            navigationType: mn.Pop,
          },
        },
        y,
      )
    : y;
}
function LE() {
  let e = HE(),
    t = TE(e)
      ? e.status + " " + e.statusText
      : e instanceof Error
        ? e.message
        : JSON.stringify(e),
    n = e instanceof Error ? e.stack : null,
    i = { padding: "0.5rem", backgroundColor: "rgba(200,200,200, 0.5)" };
  return D.createElement(
    D.Fragment,
    null,
    D.createElement("h2", null, "Unexpected Application Error!"),
    D.createElement("h3", { style: { fontStyle: "italic" } }, t),
    n ? D.createElement("pre", { style: i }, n) : null,
    null,
  );
}
const DE = D.createElement(LE, null);
class PE extends D.Component {
  constructor(t) {
    (super(t),
      (this.state = {
        location: t.location,
        revalidation: t.revalidation,
        error: t.error,
      }));
  }
  static getDerivedStateFromError(t) {
    return { error: t };
  }
  static getDerivedStateFromProps(t, n) {
    return n.location !== t.location ||
      (n.revalidation !== "idle" && t.revalidation === "idle")
      ? { error: t.error, location: t.location, revalidation: t.revalidation }
      : {
          error: t.error !== void 0 ? t.error : n.error,
          location: n.location,
          revalidation: t.revalidation || n.revalidation,
        };
  }
  componentDidCatch(t, n) {
    console.error(
      "React Router caught the following error during render",
      t,
      n,
    );
  }
  render() {
    return this.state.error !== void 0
      ? D.createElement(
          er.Provider,
          { value: this.props.routeContext },
          D.createElement(Ig.Provider, {
            value: this.state.error,
            children: this.props.component,
          }),
        )
      : this.props.children;
  }
}
function zE(e) {
  let { routeContext: t, match: n, children: r } = e,
    i = D.useContext(Ju);
  return (
    i &&
      i.static &&
      i.staticContext &&
      (n.route.errorElement || n.route.ErrorBoundary) &&
      (i.staticContext._deepestRenderedBoundaryId = n.route.id),
    D.createElement(er.Provider, { value: t }, r)
  );
}
function FE(e, t, n, r) {
  var i;
  if (
    (t === void 0 && (t = []),
    n === void 0 && (n = null),
    r === void 0 && (r = null),
    e == null)
  ) {
    var o;
    if (!n) return null;
    if (n.errors) e = n.matches;
    else if (
      (o = r) != null &&
      o.v7_partialHydration &&
      t.length === 0 &&
      !n.initialized &&
      n.matches.length > 0
    )
      e = n.matches;
    else return null;
  }
  let l = e,
    a = (i = n) == null ? void 0 : i.errors;
  if (a != null) {
    let d = l.findIndex(
      (c) => c.route.id && (a == null ? void 0 : a[c.route.id]) !== void 0,
    );
    (d >= 0 || Ce(!1), (l = l.slice(0, Math.min(l.length, d + 1))));
  }
  let s = !1,
    u = -1;
  if (n && r && r.v7_partialHydration)
    for (let d = 0; d < l.length; d++) {
      let c = l[d];
      if (
        ((c.route.HydrateFallback || c.route.hydrateFallbackElement) && (u = d),
        c.route.id)
      ) {
        let { loaderData: f, errors: p } = n,
          g =
            c.route.loader &&
            f[c.route.id] === void 0 &&
            (!p || p[c.route.id] === void 0);
        if (c.route.lazy || g) {
          ((s = !0), u >= 0 ? (l = l.slice(0, u + 1)) : (l = [l[0]]));
          break;
        }
      }
    }
  return l.reduceRight((d, c, f) => {
    let p,
      g = !1,
      y = null,
      E = null;
    n &&
      ((p = a && c.route.id ? a[c.route.id] : void 0),
      (y = c.route.errorElement || DE),
      s &&
        (u < 0 && f === 0
          ? (WE("route-fallback"), (g = !0), (E = null))
          : u === f &&
            ((g = !0), (E = c.route.hydrateFallbackElement || null))));
    let h = t.concat(l.slice(0, f + 1)),
      m = () => {
        let b;
        return (
          p
            ? (b = y)
            : g
              ? (b = E)
              : c.route.Component
                ? (b = D.createElement(c.route.Component, null))
                : c.route.element
                  ? (b = c.route.element)
                  : (b = d),
          D.createElement(zE, {
            match: c,
            routeContext: { outlet: d, matches: h, isDataRoute: n != null },
            children: b,
          })
        );
      };
    return n && (c.route.ErrorBoundary || c.route.errorElement || f === 0)
      ? D.createElement(PE, {
          location: n.location,
          revalidation: n.revalidation,
          component: y,
          error: p,
          children: m(),
          routeContext: { outlet: null, matches: h, isDataRoute: !0 },
        })
      : m();
  }, null);
}
var Lg = (function (e) {
    return (
      (e.UseBlocker = "useBlocker"),
      (e.UseRevalidator = "useRevalidator"),
      (e.UseNavigateStable = "useNavigate"),
      e
    );
  })(Lg || {}),
  Dg = (function (e) {
    return (
      (e.UseBlocker = "useBlocker"),
      (e.UseLoaderData = "useLoaderData"),
      (e.UseActionData = "useActionData"),
      (e.UseRouteError = "useRouteError"),
      (e.UseNavigation = "useNavigation"),
      (e.UseRouteLoaderData = "useRouteLoaderData"),
      (e.UseMatches = "useMatches"),
      (e.UseRevalidator = "useRevalidator"),
      (e.UseNavigateStable = "useNavigate"),
      (e.UseRouteId = "useRouteId"),
      e
    );
  })(Dg || {});
function BE(e) {
  let t = D.useContext(Ju);
  return (t || Ce(!1), t);
}
function UE(e) {
  let t = D.useContext(RE);
  return (t || Ce(!1), t);
}
function $E(e) {
  let t = D.useContext(er);
  return (t || Ce(!1), t);
}
function Pg(e) {
  let t = $E(),
    n = t.matches[t.matches.length - 1];
  return (n.route.id || Ce(!1), n.route.id);
}
function HE() {
  var e;
  let t = D.useContext(Ig),
    n = UE(),
    r = Pg();
  return t !== void 0 ? t : (e = n.errors) == null ? void 0 : e[r];
}
function jE() {
  let { router: e } = BE(Lg.UseNavigateStable),
    t = Pg(Dg.UseNavigateStable),
    n = D.useRef(!1);
  return (
    Mg(() => {
      n.current = !0;
    }),
    D.useCallback(
      function (i, o) {
        (o === void 0 && (o = {}),
          n.current &&
            (typeof i == "number"
              ? e.navigate(i)
              : e.navigate(i, Ki({ fromRouteId: t }, o))));
      },
      [e, t],
    )
  );
}
const Hd = {};
function WE(e, t, n) {
  Hd[e] || (Hd[e] = !0);
}
function GE(e, t) {
  (e == null || e.v7_startTransition, e == null || e.v7_relativeSplatPath);
}
function KE(e) {
  let { to: t, replace: n, state: r, relative: i } = e;
  ro() || Ce(!1);
  let { future: o, static: l } = D.useContext(no),
    { matches: a } = D.useContext(er),
    { pathname: s } = ec(),
    u = tc(),
    d = Ag(t, Tg(a, o.v7_relativeSplatPath), s, i === "path"),
    c = JSON.stringify(d);
  return (
    D.useEffect(
      () => u(JSON.parse(c), { replace: n, state: r, relative: i }),
      [u, c, i, n, r],
    ),
    null
  );
}
function qo(e) {
  Ce(!1);
}
function VE(e) {
  let {
    basename: t = "/",
    children: n = null,
    location: r,
    navigationType: i = mn.Pop,
    navigator: o,
    static: l = !1,
    future: a,
  } = e;
  ro() && Ce(!1);
  let s = t.replace(/^\/*/, "/"),
    u = D.useMemo(
      () => ({
        basename: s,
        navigator: o,
        static: l,
        future: Ki({ v7_relativeSplatPath: !1 }, a),
      }),
      [s, a, o, l],
    );
  typeof r == "string" && (r = Wr(r));
  let {
      pathname: d = "/",
      search: c = "",
      hash: f = "",
      state: p = null,
      key: g = "default",
    } = r,
    y = D.useMemo(() => {
      let E = Cg(d, s);
      return E == null
        ? null
        : {
            location: { pathname: E, search: c, hash: f, state: p, key: g },
            navigationType: i,
          };
    }, [s, d, c, f, p, g, i]);
  return y == null
    ? null
    : D.createElement(
        no.Provider,
        { value: u },
        D.createElement(Vl.Provider, { children: n, value: y }),
      );
}
function qE(e) {
  let { children: t, location: n } = e;
  return IE($s(t), n);
}
new Promise(() => {});
function $s(e, t) {
  t === void 0 && (t = []);
  let n = [];
  return (
    D.Children.forEach(e, (r, i) => {
      if (!D.isValidElement(r)) return;
      let o = [...t, i];
      if (r.type === D.Fragment) {
        n.push.apply(n, $s(r.props.children, o));
        return;
      }
      (r.type !== qo && Ce(!1), !r.props.index || !r.props.children || Ce(!1));
      let l = {
        id: r.props.id || o.join("-"),
        caseSensitive: r.props.caseSensitive,
        element: r.props.element,
        Component: r.props.Component,
        index: r.props.index,
        path: r.props.path,
        loader: r.props.loader,
        action: r.props.action,
        errorElement: r.props.errorElement,
        ErrorBoundary: r.props.ErrorBoundary,
        hasErrorBoundary:
          r.props.ErrorBoundary != null || r.props.errorElement != null,
        shouldRevalidate: r.props.shouldRevalidate,
        handle: r.props.handle,
        lazy: r.props.lazy,
      };
      (r.props.children && (l.children = $s(r.props.children, o)), n.push(l));
    }),
    n
  );
}
/**
 * React Router DOM v6.30.4
 *
 * Copyright (c) Remix Software Inc.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE.md file in the root directory of this source tree.
 *
 * @license MIT
 */ const YE = "6";
try {
  window.__reactRouterVersion = YE;
} catch {}
const QE = "startTransition",
  jd = Gy[QE];
function ZE(e) {
  let { basename: t, children: n, future: r, window: i } = e,
    o = D.useRef();
  o.current == null && (o.current = rE({ window: i, v5Compat: !0 }));
  let l = o.current,
    [a, s] = D.useState({ action: l.action, location: l.location }),
    { v7_startTransition: u } = r || {},
    d = D.useCallback(
      (c) => {
        u && jd ? jd(() => s(c)) : s(c);
      },
      [s, u],
    );
  return (
    D.useLayoutEffect(() => l.listen(d), [l, d]),
    D.useEffect(() => GE(r), [r]),
    D.createElement(VE, {
      basename: t,
      children: n,
      location: a.location,
      navigationType: a.action,
      navigator: l,
      future: r,
    })
  );
}
var Wd;
(function (e) {
  ((e.UseScrollRestoration = "useScrollRestoration"),
    (e.UseSubmit = "useSubmit"),
    (e.UseSubmitFetcher = "useSubmitFetcher"),
    (e.UseFetcher = "useFetcher"),
    (e.useViewTransitionState = "useViewTransitionState"));
})(Wd || (Wd = {}));
var Gd;
(function (e) {
  ((e.UseFetcher = "useFetcher"),
    (e.UseFetchers = "useFetchers"),
    (e.UseScrollRestoration = "useScrollRestoration"));
})(Gd || (Gd = {}));
const Hs = "/api";
function js() {
  return localStorage.getItem("token");
}
async function ln(e, t = {}) {
  const n = { ...t.headers },
    r = js();
  (r && (n.Authorization = `Bearer ${r}`),
    t.body &&
      typeof t.body == "string" &&
      (n["Content-Type"] = "application/json"));
  const i = await fetch(`${Hs}${e}`, { ...t, headers: n });
  return (
    i.status === 401 &&
      !e.startsWith("/auth/") &&
      (localStorage.removeItem("token"),
      localStorage.removeItem("user"),
      window.location.reload()),
    i
  );
}
const Yt = {
  login: (e, t) =>
    ln("/auth/login", {
      method: "POST",
      body: JSON.stringify({ email: e, password: t }),
    }),
  guest: () => ln("/auth/guest", { method: "POST", body: "{}" }),
  register: (e, t, n) =>
    ln("/auth/register", {
      method: "POST",
      body: JSON.stringify({ email: e, password: t, display_name: n }),
    }),
  listSessions: () => ln("/sessions/"),
  createSession: () => ln("/sessions/", { method: "POST" }),
  deleteSession: (e) => ln(`/sessions/${e}`, { method: "DELETE" }),
  chatStream: (e, t) =>
    fetch(`${Hs}/chat/stream`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${js()}`,
      },
      body: JSON.stringify({ session_id: e, message: t }),
    }),
  search: (e, t = 5) => ln(`/rag/search?q=${encodeURIComponent(e)}&top_k=${t}`),
  getMessages: (e) => ln(`/sessions/${e}/messages`),
  upload: (e) => {
    const t = new FormData();
    return (
      t.append("file", e),
      fetch(`${Hs}/files/upload`, {
        method: "POST",
        headers: { Authorization: `Bearer ${js()}` },
        body: t,
      })
    );
  },
};
/**
 * @license lucide-react v0.400.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */ const XE = (e) => e.replace(/([a-z0-9])([A-Z])/g, "$1-$2").toLowerCase(),
  zg = (...e) => e.filter((t, n, r) => !!t && r.indexOf(t) === n).join(" ");
/**
 * @license lucide-react v0.400.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */ var JE = {
  xmlns: "http://www.w3.org/2000/svg",
  width: 24,
  height: 24,
  viewBox: "0 0 24 24",
  fill: "none",
  stroke: "currentColor",
  strokeWidth: 2,
  strokeLinecap: "round",
  strokeLinejoin: "round",
};
/**
 * @license lucide-react v0.400.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */ const ew = D.forwardRef(
  (
    {
      color: e = "currentColor",
      size: t = 24,
      strokeWidth: n = 2,
      absoluteStrokeWidth: r,
      className: i = "",
      children: o,
      iconNode: l,
      ...a
    },
    s,
  ) =>
    D.createElement(
      "svg",
      {
        ref: s,
        ...JE,
        width: t,
        height: t,
        stroke: e,
        strokeWidth: r ? (Number(n) * 24) / Number(t) : n,
        className: zg("lucide", i),
        ...a,
      },
      [
        ...l.map(([u, d]) => D.createElement(u, d)),
        ...(Array.isArray(o) ? o : [o]),
      ],
    ),
);
/**
 * @license lucide-react v0.400.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */ const At = (e, t) => {
  const n = D.forwardRef(({ className: r, ...i }, o) =>
    D.createElement(ew, {
      ref: o,
      iconNode: t,
      className: zg(`lucide-${XE(e)}`, r),
      ...i,
    }),
  );
  return ((n.displayName = `${e}`), n);
};
/**
 * @license lucide-react v0.400.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */ const tw = At("ArrowRight", [
  ["path", { d: "M5 12h14", key: "1ays0h" }],
  ["path", { d: "m12 5 7 7-7 7", key: "xquz4c" }],
]);
/**
 * @license lucide-react v0.400.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */ const nw = At("BookOpen", [
  ["path", { d: "M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z", key: "vv98re" }],
  ["path", { d: "M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z", key: "1cyq3y" }],
]);
/**
 * @license lucide-react v0.400.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */ const xl = At("GraduationCap", [
  [
    "path",
    {
      d: "M21.42 10.922a1 1 0 0 0-.019-1.838L12.83 5.18a2 2 0 0 0-1.66 0L2.6 9.08a1 1 0 0 0 0 1.832l8.57 3.908a2 2 0 0 0 1.66 0z",
      key: "j76jl0",
    },
  ],
  ["path", { d: "M22 10v6", key: "1lu8f3" }],
  ["path", { d: "M6 12.5V16a6 3 0 0 0 12 0v-3.5", key: "1r8lef" }],
]);
/**
 * @license lucide-react v0.400.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */ const rw = At("MessageSquare", [
  [
    "path",
    {
      d: "M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z",
      key: "1lielz",
    },
  ],
]);
/**
 * @license lucide-react v0.400.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */ const Kd = At("Paperclip", [
  [
    "path",
    {
      d: "m21.44 11.05-9.19 9.19a6 6 0 0 1-8.49-8.49l8.57-8.57A4 4 0 1 1 18 8.84l-8.59 8.57a2 2 0 0 1-2.83-2.83l8.49-8.48",
      key: "1u3ebp",
    },
  ],
]);
/**
 * @license lucide-react v0.400.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */ const iw = At("PenTool", [
  [
    "path",
    {
      d: "M15.707 21.293a1 1 0 0 1-1.414 0l-1.586-1.586a1 1 0 0 1 0-1.414l5.586-5.586a1 1 0 0 1 1.414 0l1.586 1.586a1 1 0 0 1 0 1.414z",
      key: "nt11vn",
    },
  ],
  [
    "path",
    {
      d: "m18 13-1.375-6.874a1 1 0 0 0-.746-.776L3.235 2.028a1 1 0 0 0-1.207 1.207L5.35 15.879a1 1 0 0 0 .776.746L13 18",
      key: "15qc1e",
    },
  ],
  ["path", { d: "m2.3 2.3 7.286 7.286", key: "1wuzzi" }],
  ["circle", { cx: "11", cy: "11", r: "2", key: "xmgehs" }],
]);
/**
 * @license lucide-react v0.400.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */ const ow = At("Plus", [
  ["path", { d: "M5 12h14", key: "1ays0h" }],
  ["path", { d: "M12 5v14", key: "s699le" }],
]);
/**
 * @license lucide-react v0.400.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */ const lw = At("Send", [
  ["path", { d: "m22 2-7 20-4-9-9-4Z", key: "1q3vgg" }],
  ["path", { d: "M22 2 11 13", key: "nzbqef" }],
]);
/**
 * @license lucide-react v0.400.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */ const nc = At("Sparkles", [
  [
    "path",
    {
      d: "M9.937 15.5A2 2 0 0 0 8.5 14.063l-6.135-1.582a.5.5 0 0 1 0-.962L8.5 9.936A2 2 0 0 0 9.937 8.5l1.582-6.135a.5.5 0 0 1 .963 0L14.063 8.5A2 2 0 0 0 15.5 9.937l6.135 1.581a.5.5 0 0 1 0 .964L15.5 14.063a2 2 0 0 0-1.437 1.437l-1.582 6.135a.5.5 0 0 1-.963 0z",
      key: "4pj2yx",
    },
  ],
  ["path", { d: "M20 3v4", key: "1olli1" }],
  ["path", { d: "M22 5h-4", key: "1gvqau" }],
  ["path", { d: "M4 17v2", key: "vumght" }],
  ["path", { d: "M5 18H3", key: "zchphs" }],
]);
/**
 * @license lucide-react v0.400.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */ const aw = At("Trash2", [
  ["path", { d: "M3 6h18", key: "d0wm0j" }],
  ["path", { d: "M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6", key: "4alrt4" }],
  ["path", { d: "M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2", key: "v07s0e" }],
  ["line", { x1: "10", x2: "10", y1: "11", y2: "17", key: "1uufr5" }],
  ["line", { x1: "14", x2: "14", y1: "11", y2: "17", key: "xtxkd" }],
]);
/**
 * @license lucide-react v0.400.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */ const sw = At("X", [
  ["path", { d: "M18 6 6 18", key: "1bl5f8" }],
  ["path", { d: "m6 6 12 12", key: "d8bk6v" }],
]);
/**
 * WirelessAgent work-section icons
 */
const WkSearch = At("Search", [
  ["circle", { cx: "11", cy: "11", r: "8", key: "wk-s1" }],
  ["path", { d: "m21 21-4.3-4.3", key: "wk-s2" }],
]);
const WkUpload = At("Upload", [
  ["path", { d: "M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4", key: "wk-u1" }],
  ["polyline", { points: "17 8 12 3 7 8", key: "wk-u2" }],
  ["line", { x1: "12", y1: "3", x2: "12", y2: "15", key: "wk-u3" }],
]);
const WkBriefcase = At("Briefcase", [
  ["path", { d: "M16 20V4a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16", key: "wk-b1" }],
  ["rect", { width: "20", height: "14", x: "2", y: "6", rx: "2", key: "wk-b2" }],
]);
const WkPaper = At("Newspaper", [
  ["path", { d: "M4 22h16a2 2 0 0 0 2-2V4a2 2 0 0 0-2-2H8a2 2 0 0 0-2 2v16a2 2 0 0 1-2 2Zm0 0a2 2 0 0 1-2-2v-9a2 2 0 0 1 2-2h2", key: "wk-p1" }],
  ["path", { d: "M18 14h-8", key: "wk-p2" }],
  ["path", { d: "M15 18h-5", key: "wk-p3" }],
  ["path", { d: "M10 6h8v4h-8Z", key: "wk-p4" }],
]);
function uw() {
  const [e, t] = D.useState(""),
    [n, r] = D.useState(""),
    [i, o] = D.useState(""),
    [l, a] = D.useState(!1),
    [s, u] = D.useState(""),
    d = tc(),
    c = async (f) => {
      (f.preventDefault(), u(""));
      try {
        const p = l
          ? await Yt.register(e, n, i || e.split("@")[0])
          : await Yt.login(e, n);
        if (p.ok) {
          const g = await p.json();
          (localStorage.setItem("token", g.access_token),
            localStorage.setItem(
              "user",
              JSON.stringify({ id: g.user_id, name: g.display_name }),
            ),
            d("/"));
        } else {
          const g = await p.json();
          u(g.detail || "认证失败");
        }
      } catch {
        u("Cannot connect to server");
      }
    };
  return T.jsxs("div", {
    className:
      "min-h-screen flex bg-gradient-to-br from-cream-50 via-cream-100 to-lavender-100",
    children: [
      T.jsxs("div", {
        className:
          "hidden lg:flex flex-1 items-center justify-center relative overflow-hidden",
        children: [
          T.jsx("div", { className: "absolute inset-0 welcome-grid" }),
          T.jsxs("div", {
            className: "relative z-10 text-center",
            children: [
              T.jsx("div", {
                className:
                  "w-20 h-20 mx-auto mb-6 bg-white rounded-3xl p-4 shadow-xl shadow-orange-100 border border-cream-200",
                children: T.jsx(xl, {
                  className: "w-full h-full text-sunset-500",
                }),
              }),
              T.jsx("h1", {
                className: "text-4xl font-brand text-foreground mb-3",
                children: "WirelessAgent",
              }),
              T.jsxs("p", {
                className:
                  "text-muted-foreground text-sm leading-relaxed max-w-xs mx-auto",
                children: [
                  "Your 24/7 Wireless AI Assistant",
                  T.jsx("br", {}),
                  "习题解答 Â· 标准检索 Â· 论文速递 Â· 网规辅助",
                ],
              }),
            ],
          }),
        ],
      }),
      T.jsx("div", {
        className: "flex-1 flex items-center justify-center px-8",
        children: T.jsxs("div", {
          className: "w-full max-w-sm",
          children: [
            T.jsxs("div", {
              className: "lg:hidden text-center mb-8",
              children: [
                T.jsx("div", {
                  className:
                    "w-14 h-14 mx-auto mb-3 bg-white rounded-2xl p-3 shadow-lg shadow-orange-100 border border-cream-200",
                  children: T.jsx(xl, {
                    className: "w-full h-full text-sunset-500",
                  }),
                }),
                T.jsx("h1", {
                  className: "text-2xl font-brand text-foreground",
                  children: "WirelessAgent",
                }),
              ],
            }),
            T.jsx("h2", {
              className: "text-xl font-bold text-foreground mb-1",
              children: l ? "Register" : "Welcome back",
            }),
            T.jsx("p", {
              className: "text-sm text-muted-foreground mb-6",
              children: l
                ? "Start your wireless learning journey"
                : "Continue your progress",
            }),
            T.jsxs("form", {
              onSubmit: c,
              className: "space-y-3.5",
              children: [
                l &&
                  T.jsx("input", {
                    type: "text",
                    value: i,
                    onChange: (f) => o(f.target.value),
                    placeholder: "昵称",
                    className: `w-full bg-white border border-cream-300 rounded-2xl px-4 py-3 text-sm\r
                           placeholder:text-muted-foreground/50 focus:outline-none focus:ring-2 focus:ring-sunset-400/30\r
                           focus:border-sunset-400 transition-all`,
                  }),
                T.jsx("input", {
                  type: "email",
                  value: e,
                  onChange: (f) => t(f.target.value),
                  placeholder: "邮箱",
                  required: !0,
                  className: `w-full bg-white border border-cream-300 rounded-2xl px-4 py-3 text-sm\r
                         placeholder:text-muted-foreground/50 focus:outline-none focus:ring-2 focus:ring-sunset-400/30\r
                         focus:border-sunset-400 transition-all`,
                }),
                T.jsx("input", {
                  type: "password",
                  value: n,
                  onChange: (f) => r(f.target.value),
                  placeholder: "密码",
                  required: !0,
                  minLength: 6,
                  className: `w-full bg-white border border-cream-300 rounded-2xl px-4 py-3 text-sm\r
                         placeholder:text-muted-foreground/50 focus:outline-none focus:ring-2 focus:ring-sunset-400/30\r
                         focus:border-sunset-400 transition-all`,
                }),
                s &&
                  T.jsx("p", {
                    className:
                      "text-red-400 text-xs bg-red-50 rounded-xl px-3 py-2",
                    children: s,
                  }),
                T.jsxs("button", {
                  type: "submit",
                  className: `w-full flex items-center justify-center gap-2 bg-sunset-500 hover:bg-sunset-600\r
                         text-white rounded-2xl py-3 text-sm font-semibold transition-all duration-200\r
                         shadow-md shadow-orange-200 hover:shadow-lg hover:shadow-orange-200 active:scale-[0.98]`,
                  children: [
                    l ? "Register" : "Login",
                    T.jsx(tw, { className: "w-4 h-4" }),
                  ],
                }),
              ],
            }),
            T.jsxs("p", {
              className: "text-center text-muted-foreground/60 text-xs mt-5",
              children: [
                l ? "Already registered?" : "No account?",
                T.jsx("button", {
                  onClick: () => {
                    (a(!l), u(""));
                  },
                  className:
                    "text-sunset-500 hover:text-sunset-600 font-medium ml-1.5 transition-colors",
                  children: l ? "Login" : "Register free",
                }),
              ],
            }),
            T.jsx("div", {
              className: "mt-4 text-center",
              children: T.jsx("button", {
                onClick: async () => {
                  try {
                    const f = await Yt.guest();
                    if (f.ok) {
                      const p = await f.json();
                      (localStorage.setItem("token", p.access_token),
                        localStorage.setItem(
                          "user",
                          JSON.stringify({
                            id: p.user_id,
                            name: p.display_name,
                          }),
                        ),
                        d("/"));
                    }
                  } catch {}
                },
                className:
                  "text-muted-foreground/40 hover:text-sunset-500 text-xs transition-colors",
                children: "跳过登录，直接使用",
              }),
            }),
            T.jsxs("div", {
              className: "mt-8 flex items-center gap-2 justify-center",
              children: [
                T.jsx(nc, { className: "w-3.5 h-3.5 text-lavender-400" }),
                T.jsx("span", {
                  className: "text-xs text-muted-foreground/40",
                  children: "Secured - local storage",
                }),
              ],
            }),
          ],
        }),
      }),
    ],
  });
}
function Fg(e) {
  var t,
    n,
    r = "";
  if (typeof e == "string" || typeof e == "number") r += e;
  else if (typeof e == "object")
    if (Array.isArray(e)) {
      var i = e.length;
      for (t = 0; t < i; t++)
        e[t] && (n = Fg(e[t])) && (r && (r += " "), (r += n));
    } else for (n in e) e[n] && (r && (r += " "), (r += n));
  return r;
}
function cw() {
  for (var e, t, n = 0, r = "", i = arguments.length; n < i; n++)
    (e = arguments[n]) && (t = Fg(e)) && (r && (r += " "), (r += t));
  return r;
}
const rc = "-",
  dw = (e) => {
    const t = pw(e),
      { conflictingClassGroups: n, conflictingClassGroupModifiers: r } = e;
    return {
      getClassGroupId: (l) => {
        const a = l.split(rc);
        return (a[0] === "" && a.length !== 1 && a.shift(), Bg(a, t) || fw(l));
      },
      getConflictingClassGroupIds: (l, a) => {
        const s = n[l] || [];
        return a && r[l] ? [...s, ...r[l]] : s;
      },
    };
  },
  Bg = (e, t) => {
    var l;
    if (e.length === 0) return t.classGroupId;
    const n = e[0],
      r = t.nextPart.get(n),
      i = r ? Bg(e.slice(1), r) : void 0;
    if (i) return i;
    if (t.validators.length === 0) return;
    const o = e.join(rc);
    return (l = t.validators.find(({ validator: a }) => a(o))) == null
      ? void 0
      : l.classGroupId;
  },
  Vd = /^\[(.+)\]$/,
  fw = (e) => {
    if (Vd.test(e)) {
      const t = Vd.exec(e)[1],
        n = t == null ? void 0 : t.substring(0, t.indexOf(":"));
      if (n) return "arbitrary.." + n;
    }
  },
  pw = (e) => {
    const { theme: t, prefix: n } = e,
      r = { nextPart: new Map(), validators: [] };
    return (
      gw(Object.entries(e.classGroups), n).forEach(([o, l]) => {
        Ws(l, r, o, t);
      }),
      r
    );
  },
  Ws = (e, t, n, r) => {
    e.forEach((i) => {
      if (typeof i == "string") {
        const o = i === "" ? t : qd(t, i);
        o.classGroupId = n;
        return;
      }
      if (typeof i == "function") {
        if (hw(i)) {
          Ws(i(r), t, n, r);
          return;
        }
        t.validators.push({ validator: i, classGroupId: n });
        return;
      }
      Object.entries(i).forEach(([o, l]) => {
        Ws(l, qd(t, o), n, r);
      });
    });
  },
  qd = (e, t) => {
    let n = e;
    return (
      t.split(rc).forEach((r) => {
        (n.nextPart.has(r) ||
          n.nextPart.set(r, { nextPart: new Map(), validators: [] }),
          (n = n.nextPart.get(r)));
      }),
      n
    );
  },
  hw = (e) => e.isThemeGetter,
  gw = (e, t) =>
    t
      ? e.map(([n, r]) => {
          const i = r.map((o) =>
            typeof o == "string"
              ? t + o
              : typeof o == "object"
                ? Object.fromEntries(
                    Object.entries(o).map(([l, a]) => [t + l, a]),
                  )
                : o,
          );
          return [n, i];
        })
      : e,
  mw = (e) => {
    if (e < 1) return { get: () => {}, set: () => {} };
    let t = 0,
      n = new Map(),
      r = new Map();
    const i = (o, l) => {
      (n.set(o, l), t++, t > e && ((t = 0), (r = n), (n = new Map())));
    };
    return {
      get(o) {
        let l = n.get(o);
        if (l !== void 0) return l;
        if ((l = r.get(o)) !== void 0) return (i(o, l), l);
      },
      set(o, l) {
        n.has(o) ? n.set(o, l) : i(o, l);
      },
    };
  },
  Ug = "!",
  yw = (e) => {
    const { separator: t, experimentalParseClassName: n } = e,
      r = t.length === 1,
      i = t[0],
      o = t.length,
      l = (a) => {
        const s = [];
        let u = 0,
          d = 0,
          c;
        for (let E = 0; E < a.length; E++) {
          let h = a[E];
          if (u === 0) {
            if (h === i && (r || a.slice(E, E + o) === t)) {
              (s.push(a.slice(d, E)), (d = E + o));
              continue;
            }
            if (h === "/") {
              c = E;
              continue;
            }
          }
          h === "[" ? u++ : h === "]" && u--;
        }
        const f = s.length === 0 ? a : a.substring(d),
          p = f.startsWith(Ug),
          g = p ? f.substring(1) : f,
          y = c && c > d ? c - d : void 0;
        return {
          modifiers: s,
          hasImportantModifier: p,
          baseClassName: g,
          maybePostfixModifierPosition: y,
        };
      };
    return n ? (a) => n({ className: a, parseClassName: l }) : l;
  },
  bw = (e) => {
    if (e.length <= 1) return e;
    const t = [];
    let n = [];
    return (
      e.forEach((r) => {
        r[0] === "[" ? (t.push(...n.sort(), r), (n = [])) : n.push(r);
      }),
      t.push(...n.sort()),
      t
    );
  },
  vw = (e) => ({ cache: mw(e.cacheSize), parseClassName: yw(e), ...dw(e) }),
  Ew = /\s+/,
  ww = (e, t) => {
    const {
        parseClassName: n,
        getClassGroupId: r,
        getConflictingClassGroupIds: i,
      } = t,
      o = [],
      l = e.trim().split(Ew);
    let a = "";
    for (let s = l.length - 1; s >= 0; s -= 1) {
      const u = l[s],
        {
          modifiers: d,
          hasImportantModifier: c,
          baseClassName: f,
          maybePostfixModifierPosition: p,
        } = n(u);
      let g = !!p,
        y = r(g ? f.substring(0, p) : f);
      if (!y) {
        if (!g) {
          a = u + (a.length > 0 ? " " + a : a);
          continue;
        }
        if (((y = r(f)), !y)) {
          a = u + (a.length > 0 ? " " + a : a);
          continue;
        }
        g = !1;
      }
      const E = bw(d).join(":"),
        h = c ? E + Ug : E,
        m = h + y;
      if (o.includes(m)) continue;
      o.push(m);
      const b = i(y, g);
      for (let _ = 0; _ < b.length; ++_) {
        const N = b[_];
        o.push(h + N);
      }
      a = u + (a.length > 0 ? " " + a : a);
    }
    return a;
  };
function xw() {
  let e = 0,
    t,
    n,
    r = "";
  for (; e < arguments.length;)
    (t = arguments[e++]) && (n = $g(t)) && (r && (r += " "), (r += n));
  return r;
}
const $g = (e) => {
  if (typeof e == "string") return e;
  let t,
    n = "";
  for (let r = 0; r < e.length; r++)
    e[r] && (t = $g(e[r])) && (n && (n += " "), (n += t));
  return n;
};
function _w(e, ...t) {
  let n,
    r,
    i,
    o = l;
  function l(s) {
    const u = t.reduce((d, c) => c(d), e());
    return ((n = vw(u)), (r = n.cache.get), (i = n.cache.set), (o = a), a(s));
  }
  function a(s) {
    const u = r(s);
    if (u) return u;
    const d = ww(s, n);
    return (i(s, d), d);
  }
  return function () {
    return o(xw.apply(null, arguments));
  };
}
const he = (e) => {
    const t = (n) => n[e] || [];
    return ((t.isThemeGetter = !0), t);
  },
  Hg = /^\[(?:([a-z-]+):)?(.+)\]$/i,
  kw = /^\d+\/\d+$/,
  Sw = new Set(["px", "full", "screen"]),
  Nw = /^(\d+(\.\d+)?)?(xs|sm|md|lg|xl)$/,
  Cw =
    /\d+(%|px|r?em|[sdl]?v([hwib]|min|max)|pt|pc|in|cm|mm|cap|ch|ex|r?lh|cq(w|h|i|b|min|max))|\b(calc|min|max|clamp)\(.+\)|^0$/,
  Tw = /^(rgba?|hsla?|hwb|(ok)?(lab|lch)|color-mix)\(.+\)$/,
  Aw = /^(inset_)?-?((\d+)?\.?(\d+)[a-z]+|0)_-?((\d+)?\.?(\d+)[a-z]+|0)/,
  Rw =
    /^(url|image|image-set|cross-fade|element|(repeating-)?(linear|radial|conic)-gradient)\(.+\)$/,
  jt = (e) => Rr(e) || Sw.has(e) || kw.test(e),
  an = (e) => Gr(e, "length", Fw),
  Rr = (e) => !!e && !Number.isNaN(Number(e)),
  Ta = (e) => Gr(e, "number", Rr),
  ai = (e) => !!e && Number.isInteger(Number(e)),
  Ow = (e) => e.endsWith("%") && Rr(e.slice(0, -1)),
  J = (e) => Hg.test(e),
  sn = (e) => Nw.test(e),
  Iw = new Set(["length", "size", "percentage"]),
  Mw = (e) => Gr(e, Iw, jg),
  Lw = (e) => Gr(e, "position", jg),
  Dw = new Set(["image", "url"]),
  Pw = (e) => Gr(e, Dw, Uw),
  zw = (e) => Gr(e, "", Bw),
  si = () => !0,
  Gr = (e, t, n) => {
    const r = Hg.exec(e);
    return r
      ? r[1]
        ? typeof t == "string"
          ? r[1] === t
          : t.has(r[1])
        : n(r[2])
      : !1;
  },
  Fw = (e) => Cw.test(e) && !Tw.test(e),
  jg = () => !1,
  Bw = (e) => Aw.test(e),
  Uw = (e) => Rw.test(e),
  $w = () => {
    const e = he("colors"),
      t = he("spacing"),
      n = he("blur"),
      r = he("brightness"),
      i = he("borderColor"),
      o = he("borderRadius"),
      l = he("borderSpacing"),
      a = he("borderWidth"),
      s = he("contrast"),
      u = he("grayscale"),
      d = he("hueRotate"),
      c = he("invert"),
      f = he("gap"),
      p = he("gradientColorStops"),
      g = he("gradientColorStopPositions"),
      y = he("inset"),
      E = he("margin"),
      h = he("opacity"),
      m = he("padding"),
      b = he("saturate"),
      _ = he("scale"),
      N = he("sepia"),
      x = he("skew"),
      O = he("space"),
      I = he("translate"),
      U = () => ["auto", "contain", "none"],
      S = () => ["auto", "hidden", "clip", "visible", "scroll"],
      F = () => ["auto", J, t],
      L = () => [J, t],
      Q = () => ["", jt, an],
      V = () => ["auto", Rr, J],
      G = () => [
        "bottom",
        "center",
        "left",
        "left-bottom",
        "left-top",
        "right",
        "right-bottom",
        "right-top",
        "top",
      ],
      R = () => ["solid", "dashed", "dotted", "double", "none"],
      B = () => [
        "normal",
        "multiply",
        "screen",
        "overlay",
        "darken",
        "lighten",
        "color-dodge",
        "color-burn",
        "hard-light",
        "soft-light",
        "difference",
        "exclusion",
        "hue",
        "saturation",
        "color",
        "luminosity",
      ],
      C = () => [
        "start",
        "end",
        "center",
        "between",
        "around",
        "evenly",
        "stretch",
      ],
      M = () => ["", "0", J],
      v = () => [
        "auto",
        "avoid",
        "all",
        "avoid-page",
        "page",
        "left",
        "right",
        "column",
      ],
      H = () => [Rr, J];
    return {
      cacheSize: 500,
      separator: ":",
      theme: {
        colors: [si],
        spacing: [jt, an],
        blur: ["none", "", sn, J],
        brightness: H(),
        borderColor: [e],
        borderRadius: ["none", "", "full", sn, J],
        borderSpacing: L(),
        borderWidth: Q(),
        contrast: H(),
        grayscale: M(),
        hueRotate: H(),
        invert: M(),
        gap: L(),
        gradientColorStops: [e],
        gradientColorStopPositions: [Ow, an],
        inset: F(),
        margin: F(),
        opacity: H(),
        padding: L(),
        saturate: H(),
        scale: H(),
        sepia: M(),
        skew: H(),
        space: L(),
        translate: L(),
      },
      classGroups: {
        aspect: [{ aspect: ["auto", "square", "video", J] }],
        container: ["container"],
        columns: [{ columns: [sn] }],
        "break-after": [{ "break-after": v() }],
        "break-before": [{ "break-before": v() }],
        "break-inside": [
          { "break-inside": ["auto", "avoid", "avoid-page", "avoid-column"] },
        ],
        "box-decoration": [{ "box-decoration": ["slice", "clone"] }],
        box: [{ box: ["border", "content"] }],
        display: [
          "block",
          "inline-block",
          "inline",
          "flex",
          "inline-flex",
          "table",
          "inline-table",
          "table-caption",
          "table-cell",
          "table-column",
          "table-column-group",
          "table-footer-group",
          "table-header-group",
          "table-row-group",
          "table-row",
          "flow-root",
          "grid",
          "inline-grid",
          "contents",
          "list-item",
          "hidden",
        ],
        float: [{ float: ["right", "left", "none", "start", "end"] }],
        clear: [{ clear: ["left", "right", "both", "none", "start", "end"] }],
        isolation: ["isolate", "isolation-auto"],
        "object-fit": [
          { object: ["contain", "cover", "fill", "none", "scale-down"] },
        ],
        "object-position": [{ object: [...G(), J] }],
        overflow: [{ overflow: S() }],
        "overflow-x": [{ "overflow-x": S() }],
        "overflow-y": [{ "overflow-y": S() }],
        overscroll: [{ overscroll: U() }],
        "overscroll-x": [{ "overscroll-x": U() }],
        "overscroll-y": [{ "overscroll-y": U() }],
        position: ["static", "fixed", "absolute", "relative", "sticky"],
        inset: [{ inset: [y] }],
        "inset-x": [{ "inset-x": [y] }],
        "inset-y": [{ "inset-y": [y] }],
        start: [{ start: [y] }],
        end: [{ end: [y] }],
        top: [{ top: [y] }],
        right: [{ right: [y] }],
        bottom: [{ bottom: [y] }],
        left: [{ left: [y] }],
        visibility: ["visible", "invisible", "collapse"],
        z: [{ z: ["auto", ai, J] }],
        basis: [{ basis: F() }],
        "flex-direction": [
          { flex: ["row", "row-reverse", "col", "col-reverse"] },
        ],
        "flex-wrap": [{ flex: ["wrap", "wrap-reverse", "nowrap"] }],
        flex: [{ flex: ["1", "auto", "initial", "none", J] }],
        grow: [{ grow: M() }],
        shrink: [{ shrink: M() }],
        order: [{ order: ["first", "last", "none", ai, J] }],
        "grid-cols": [{ "grid-cols": [si] }],
        "col-start-end": [{ col: ["auto", { span: ["full", ai, J] }, J] }],
        "col-start": [{ "col-start": V() }],
        "col-end": [{ "col-end": V() }],
        "grid-rows": [{ "grid-rows": [si] }],
        "row-start-end": [{ row: ["auto", { span: [ai, J] }, J] }],
        "row-start": [{ "row-start": V() }],
        "row-end": [{ "row-end": V() }],
        "grid-flow": [
          { "grid-flow": ["row", "col", "dense", "row-dense", "col-dense"] },
        ],
        "auto-cols": [{ "auto-cols": ["auto", "min", "max", "fr", J] }],
        "auto-rows": [{ "auto-rows": ["auto", "min", "max", "fr", J] }],
        gap: [{ gap: [f] }],
        "gap-x": [{ "gap-x": [f] }],
        "gap-y": [{ "gap-y": [f] }],
        "justify-content": [{ justify: ["normal", ...C()] }],
        "justify-items": [
          { "justify-items": ["start", "end", "center", "stretch"] },
        ],
        "justify-self": [
          { "justify-self": ["auto", "start", "end", "center", "stretch"] },
        ],
        "align-content": [{ content: ["normal", ...C(), "baseline"] }],
        "align-items": [
          { items: ["start", "end", "center", "baseline", "stretch"] },
        ],
        "align-self": [
          { self: ["auto", "start", "end", "center", "stretch", "baseline"] },
        ],
        "place-content": [{ "place-content": [...C(), "baseline"] }],
        "place-items": [
          { "place-items": ["start", "end", "center", "baseline", "stretch"] },
        ],
        "place-self": [
          { "place-self": ["auto", "start", "end", "center", "stretch"] },
        ],
        p: [{ p: [m] }],
        px: [{ px: [m] }],
        py: [{ py: [m] }],
        ps: [{ ps: [m] }],
        pe: [{ pe: [m] }],
        pt: [{ pt: [m] }],
        pr: [{ pr: [m] }],
        pb: [{ pb: [m] }],
        pl: [{ pl: [m] }],
        m: [{ m: [E] }],
        mx: [{ mx: [E] }],
        my: [{ my: [E] }],
        ms: [{ ms: [E] }],
        me: [{ me: [E] }],
        mt: [{ mt: [E] }],
        mr: [{ mr: [E] }],
        mb: [{ mb: [E] }],
        ml: [{ ml: [E] }],
        "space-x": [{ "space-x": [O] }],
        "space-x-reverse": ["space-x-reverse"],
        "space-y": [{ "space-y": [O] }],
        "space-y-reverse": ["space-y-reverse"],
        w: [{ w: ["auto", "min", "max", "fit", "svw", "lvw", "dvw", J, t] }],
        "min-w": [{ "min-w": [J, t, "min", "max", "fit"] }],
        "max-w": [
          {
            "max-w": [
              J,
              t,
              "none",
              "full",
              "min",
              "max",
              "fit",
              "prose",
              { screen: [sn] },
              sn,
            ],
          },
        ],
        h: [{ h: [J, t, "auto", "min", "max", "fit", "svh", "lvh", "dvh"] }],
        "min-h": [
          { "min-h": [J, t, "min", "max", "fit", "svh", "lvh", "dvh"] },
        ],
        "max-h": [
          { "max-h": [J, t, "min", "max", "fit", "svh", "lvh", "dvh"] },
        ],
        size: [{ size: [J, t, "auto", "min", "max", "fit"] }],
        "font-size": [{ text: ["base", sn, an] }],
        "font-smoothing": ["antialiased", "subpixel-antialiased"],
        "font-style": ["italic", "not-italic"],
        "font-weight": [
          {
            font: [
              "thin",
              "extralight",
              "light",
              "normal",
              "medium",
              "semibold",
              "bold",
              "extrabold",
              "black",
              Ta,
            ],
          },
        ],
        "font-family": [{ font: [si] }],
        "fvn-normal": ["normal-nums"],
        "fvn-ordinal": ["ordinal"],
        "fvn-slashed-zero": ["slashed-zero"],
        "fvn-figure": ["lining-nums", "oldstyle-nums"],
        "fvn-spacing": ["proportional-nums", "tabular-nums"],
        "fvn-fraction": ["diagonal-fractions", "stacked-fractions"],
        tracking: [
          {
            tracking: [
              "tighter",
              "tight",
              "normal",
              "wide",
              "wider",
              "widest",
              J,
            ],
          },
        ],
        "line-clamp": [{ "line-clamp": ["none", Rr, Ta] }],
        leading: [
          {
            leading: [
              "none",
              "tight",
              "snug",
              "normal",
              "relaxed",
              "loose",
              jt,
              J,
            ],
          },
        ],
        "list-image": [{ "list-image": ["none", J] }],
        "list-style-type": [{ list: ["none", "disc", "decimal", J] }],
        "list-style-position": [{ list: ["inside", "outside"] }],
        "placeholder-color": [{ placeholder: [e] }],
        "placeholder-opacity": [{ "placeholder-opacity": [h] }],
        "text-alignment": [
          { text: ["left", "center", "right", "justify", "start", "end"] },
        ],
        "text-color": [{ text: [e] }],
        "text-opacity": [{ "text-opacity": [h] }],
        "text-decoration": [
          "underline",
          "overline",
          "line-through",
          "no-underline",
        ],
        "text-decoration-style": [{ decoration: [...R(), "wavy"] }],
        "text-decoration-thickness": [
          { decoration: ["auto", "from-font", jt, an] },
        ],
        "underline-offset": [{ "underline-offset": ["auto", jt, J] }],
        "text-decoration-color": [{ decoration: [e] }],
        "text-transform": [
          "uppercase",
          "lowercase",
          "capitalize",
          "normal-case",
        ],
        "text-overflow": ["truncate", "text-ellipsis", "text-clip"],
        "text-wrap": [{ text: ["wrap", "nowrap", "balance", "pretty"] }],
        indent: [{ indent: L() }],
        "vertical-align": [
          {
            align: [
              "baseline",
              "top",
              "middle",
              "bottom",
              "text-top",
              "text-bottom",
              "sub",
              "super",
              J,
            ],
          },
        ],
        whitespace: [
          {
            whitespace: [
              "normal",
              "nowrap",
              "pre",
              "pre-line",
              "pre-wrap",
              "break-spaces",
            ],
          },
        ],
        break: [{ break: ["normal", "words", "all", "keep"] }],
        hyphens: [{ hyphens: ["none", "manual", "auto"] }],
        content: [{ content: ["none", J] }],
        "bg-attachment": [{ bg: ["fixed", "local", "scroll"] }],
        "bg-clip": [{ "bg-clip": ["border", "padding", "content", "text"] }],
        "bg-opacity": [{ "bg-opacity": [h] }],
        "bg-origin": [{ "bg-origin": ["border", "padding", "content"] }],
        "bg-position": [{ bg: [...G(), Lw] }],
        "bg-repeat": [
          { bg: ["no-repeat", { repeat: ["", "x", "y", "round", "space"] }] },
        ],
        "bg-size": [{ bg: ["auto", "cover", "contain", Mw] }],
        "bg-image": [
          {
            bg: [
              "none",
              { "gradient-to": ["t", "tr", "r", "br", "b", "bl", "l", "tl"] },
              Pw,
            ],
          },
        ],
        "bg-color": [{ bg: [e] }],
        "gradient-from-pos": [{ from: [g] }],
        "gradient-via-pos": [{ via: [g] }],
        "gradient-to-pos": [{ to: [g] }],
        "gradient-from": [{ from: [p] }],
        "gradient-via": [{ via: [p] }],
        "gradient-to": [{ to: [p] }],
        rounded: [{ rounded: [o] }],
        "rounded-s": [{ "rounded-s": [o] }],
        "rounded-e": [{ "rounded-e": [o] }],
        "rounded-t": [{ "rounded-t": [o] }],
        "rounded-r": [{ "rounded-r": [o] }],
        "rounded-b": [{ "rounded-b": [o] }],
        "rounded-l": [{ "rounded-l": [o] }],
        "rounded-ss": [{ "rounded-ss": [o] }],
        "rounded-se": [{ "rounded-se": [o] }],
        "rounded-ee": [{ "rounded-ee": [o] }],
        "rounded-es": [{ "rounded-es": [o] }],
        "rounded-tl": [{ "rounded-tl": [o] }],
        "rounded-tr": [{ "rounded-tr": [o] }],
        "rounded-br": [{ "rounded-br": [o] }],
        "rounded-bl": [{ "rounded-bl": [o] }],
        "border-w": [{ border: [a] }],
        "border-w-x": [{ "border-x": [a] }],
        "border-w-y": [{ "border-y": [a] }],
        "border-w-s": [{ "border-s": [a] }],
        "border-w-e": [{ "border-e": [a] }],
        "border-w-t": [{ "border-t": [a] }],
        "border-w-r": [{ "border-r": [a] }],
        "border-w-b": [{ "border-b": [a] }],
        "border-w-l": [{ "border-l": [a] }],
        "border-opacity": [{ "border-opacity": [h] }],
        "border-style": [{ border: [...R(), "hidden"] }],
        "divide-x": [{ "divide-x": [a] }],
        "divide-x-reverse": ["divide-x-reverse"],
        "divide-y": [{ "divide-y": [a] }],
        "divide-y-reverse": ["divide-y-reverse"],
        "divide-opacity": [{ "divide-opacity": [h] }],
        "divide-style": [{ divide: R() }],
        "border-color": [{ border: [i] }],
        "border-color-x": [{ "border-x": [i] }],
        "border-color-y": [{ "border-y": [i] }],
        "border-color-s": [{ "border-s": [i] }],
        "border-color-e": [{ "border-e": [i] }],
        "border-color-t": [{ "border-t": [i] }],
        "border-color-r": [{ "border-r": [i] }],
        "border-color-b": [{ "border-b": [i] }],
        "border-color-l": [{ "border-l": [i] }],
        "divide-color": [{ divide: [i] }],
        "outline-style": [{ outline: ["", ...R()] }],
        "outline-offset": [{ "outline-offset": [jt, J] }],
        "outline-w": [{ outline: [jt, an] }],
        "outline-color": [{ outline: [e] }],
        "ring-w": [{ ring: Q() }],
        "ring-w-inset": ["ring-inset"],
        "ring-color": [{ ring: [e] }],
        "ring-opacity": [{ "ring-opacity": [h] }],
        "ring-offset-w": [{ "ring-offset": [jt, an] }],
        "ring-offset-color": [{ "ring-offset": [e] }],
        shadow: [{ shadow: ["", "inner", "none", sn, zw] }],
        "shadow-color": [{ shadow: [si] }],
        opacity: [{ opacity: [h] }],
        "mix-blend": [{ "mix-blend": [...B(), "plus-lighter", "plus-darker"] }],
        "bg-blend": [{ "bg-blend": B() }],
        filter: [{ filter: ["", "none"] }],
        blur: [{ blur: [n] }],
        brightness: [{ brightness: [r] }],
        contrast: [{ contrast: [s] }],
        "drop-shadow": [{ "drop-shadow": ["", "none", sn, J] }],
        grayscale: [{ grayscale: [u] }],
        "hue-rotate": [{ "hue-rotate": [d] }],
        invert: [{ invert: [c] }],
        saturate: [{ saturate: [b] }],
        sepia: [{ sepia: [N] }],
        "backdrop-filter": [{ "backdrop-filter": ["", "none"] }],
        "backdrop-blur": [{ "backdrop-blur": [n] }],
        "backdrop-brightness": [{ "backdrop-brightness": [r] }],
        "backdrop-contrast": [{ "backdrop-contrast": [s] }],
        "backdrop-grayscale": [{ "backdrop-grayscale": [u] }],
        "backdrop-hue-rotate": [{ "backdrop-hue-rotate": [d] }],
        "backdrop-invert": [{ "backdrop-invert": [c] }],
        "backdrop-opacity": [{ "backdrop-opacity": [h] }],
        "backdrop-saturate": [{ "backdrop-saturate": [b] }],
        "backdrop-sepia": [{ "backdrop-sepia": [N] }],
        "border-collapse": [{ border: ["collapse", "separate"] }],
        "border-spacing": [{ "border-spacing": [l] }],
        "border-spacing-x": [{ "border-spacing-x": [l] }],
        "border-spacing-y": [{ "border-spacing-y": [l] }],
        "table-layout": [{ table: ["auto", "fixed"] }],
        caption: [{ caption: ["top", "bottom"] }],
        transition: [
          {
            transition: [
              "none",
              "all",
              "",
              "colors",
              "opacity",
              "shadow",
              "transform",
              J,
            ],
          },
        ],
        duration: [{ duration: H() }],
        ease: [{ ease: ["linear", "in", "out", "in-out", J] }],
        delay: [{ delay: H() }],
        animate: [{ animate: ["none", "spin", "ping", "pulse", "bounce", J] }],
        transform: [{ transform: ["", "gpu", "none"] }],
        scale: [{ scale: [_] }],
        "scale-x": [{ "scale-x": [_] }],
        "scale-y": [{ "scale-y": [_] }],
        rotate: [{ rotate: [ai, J] }],
        "translate-x": [{ "translate-x": [I] }],
        "translate-y": [{ "translate-y": [I] }],
        "skew-x": [{ "skew-x": [x] }],
        "skew-y": [{ "skew-y": [x] }],
        "transform-origin": [
          {
            origin: [
              "center",
              "top",
              "top-right",
              "right",
              "bottom-right",
              "bottom",
              "bottom-left",
              "left",
              "top-left",
              J,
            ],
          },
        ],
        accent: [{ accent: ["auto", e] }],
        appearance: [{ appearance: ["none", "auto"] }],
        cursor: [
          {
            cursor: [
              "auto",
              "default",
              "pointer",
              "wait",
              "text",
              "move",
              "help",
              "not-allowed",
              "none",
              "context-menu",
              "progress",
              "cell",
              "crosshair",
              "vertical-text",
              "alias",
              "copy",
              "no-drop",
              "grab",
              "grabbing",
              "all-scroll",
              "col-resize",
              "row-resize",
              "n-resize",
              "e-resize",
              "s-resize",
              "w-resize",
              "ne-resize",
              "nw-resize",
              "se-resize",
              "sw-resize",
              "ew-resize",
              "ns-resize",
              "nesw-resize",
              "nwse-resize",
              "zoom-in",
              "zoom-out",
              J,
            ],
          },
        ],
        "caret-color": [{ caret: [e] }],
        "pointer-events": [{ "pointer-events": ["none", "auto"] }],
        resize: [{ resize: ["none", "y", "x", ""] }],
        "scroll-behavior": [{ scroll: ["auto", "smooth"] }],
        "scroll-m": [{ "scroll-m": L() }],
        "scroll-mx": [{ "scroll-mx": L() }],
        "scroll-my": [{ "scroll-my": L() }],
        "scroll-ms": [{ "scroll-ms": L() }],
        "scroll-me": [{ "scroll-me": L() }],
        "scroll-mt": [{ "scroll-mt": L() }],
        "scroll-mr": [{ "scroll-mr": L() }],
        "scroll-mb": [{ "scroll-mb": L() }],
        "scroll-ml": [{ "scroll-ml": L() }],
        "scroll-p": [{ "scroll-p": L() }],
        "scroll-px": [{ "scroll-px": L() }],
        "scroll-py": [{ "scroll-py": L() }],
        "scroll-ps": [{ "scroll-ps": L() }],
        "scroll-pe": [{ "scroll-pe": L() }],
        "scroll-pt": [{ "scroll-pt": L() }],
        "scroll-pr": [{ "scroll-pr": L() }],
        "scroll-pb": [{ "scroll-pb": L() }],
        "scroll-pl": [{ "scroll-pl": L() }],
        "snap-align": [{ snap: ["start", "end", "center", "align-none"] }],
        "snap-stop": [{ snap: ["normal", "always"] }],
        "snap-type": [{ snap: ["none", "x", "y", "both"] }],
        "snap-strictness": [{ snap: ["mandatory", "proximity"] }],
        touch: [{ touch: ["auto", "none", "manipulation"] }],
        "touch-x": [{ "touch-pan": ["x", "left", "right"] }],
        "touch-y": [{ "touch-pan": ["y", "up", "down"] }],
        "touch-pz": ["touch-pinch-zoom"],
        select: [{ select: ["none", "text", "all", "auto"] }],
        "will-change": [
          { "will-change": ["auto", "scroll", "contents", "transform", J] },
        ],
        fill: [{ fill: [e, "none"] }],
        "stroke-w": [{ stroke: [jt, an, Ta] }],
        stroke: [{ stroke: [e, "none"] }],
        sr: ["sr-only", "not-sr-only"],
        "forced-color-adjust": [{ "forced-color-adjust": ["auto", "none"] }],
      },
      conflictingClassGroups: {
        overflow: ["overflow-x", "overflow-y"],
        overscroll: ["overscroll-x", "overscroll-y"],
        inset: [
          "inset-x",
          "inset-y",
          "start",
          "end",
          "top",
          "right",
          "bottom",
          "left",
        ],
        "inset-x": ["right", "left"],
        "inset-y": ["top", "bottom"],
        flex: ["basis", "grow", "shrink"],
        gap: ["gap-x", "gap-y"],
        p: ["px", "py", "ps", "pe", "pt", "pr", "pb", "pl"],
        px: ["pr", "pl"],
        py: ["pt", "pb"],
        m: ["mx", "my", "ms", "me", "mt", "mr", "mb", "ml"],
        mx: ["mr", "ml"],
        my: ["mt", "mb"],
        size: ["w", "h"],
        "font-size": ["leading"],
        "fvn-normal": [
          "fvn-ordinal",
          "fvn-slashed-zero",
          "fvn-figure",
          "fvn-spacing",
          "fvn-fraction",
        ],
        "fvn-ordinal": ["fvn-normal"],
        "fvn-slashed-zero": ["fvn-normal"],
        "fvn-figure": ["fvn-normal"],
        "fvn-spacing": ["fvn-normal"],
        "fvn-fraction": ["fvn-normal"],
        "line-clamp": ["display", "overflow"],
        rounded: [
          "rounded-s",
          "rounded-e",
          "rounded-t",
          "rounded-r",
          "rounded-b",
          "rounded-l",
          "rounded-ss",
          "rounded-se",
          "rounded-ee",
          "rounded-es",
          "rounded-tl",
          "rounded-tr",
          "rounded-br",
          "rounded-bl",
        ],
        "rounded-s": ["rounded-ss", "rounded-es"],
        "rounded-e": ["rounded-se", "rounded-ee"],
        "rounded-t": ["rounded-tl", "rounded-tr"],
        "rounded-r": ["rounded-tr", "rounded-br"],
        "rounded-b": ["rounded-br", "rounded-bl"],
        "rounded-l": ["rounded-tl", "rounded-bl"],
        "border-spacing": ["border-spacing-x", "border-spacing-y"],
        "border-w": [
          "border-w-s",
          "border-w-e",
          "border-w-t",
          "border-w-r",
          "border-w-b",
          "border-w-l",
        ],
        "border-w-x": ["border-w-r", "border-w-l"],
        "border-w-y": ["border-w-t", "border-w-b"],
        "border-color": [
          "border-color-s",
          "border-color-e",
          "border-color-t",
          "border-color-r",
          "border-color-b",
          "border-color-l",
        ],
        "border-color-x": ["border-color-r", "border-color-l"],
        "border-color-y": ["border-color-t", "border-color-b"],
        "scroll-m": [
          "scroll-mx",
          "scroll-my",
          "scroll-ms",
          "scroll-me",
          "scroll-mt",
          "scroll-mr",
          "scroll-mb",
          "scroll-ml",
        ],
        "scroll-mx": ["scroll-mr", "scroll-ml"],
        "scroll-my": ["scroll-mt", "scroll-mb"],
        "scroll-p": [
          "scroll-px",
          "scroll-py",
          "scroll-ps",
          "scroll-pe",
          "scroll-pt",
          "scroll-pr",
          "scroll-pb",
          "scroll-pl",
        ],
        "scroll-px": ["scroll-pr", "scroll-pl"],
        "scroll-py": ["scroll-pt", "scroll-pb"],
        touch: ["touch-x", "touch-y", "touch-pz"],
        "touch-x": ["touch"],
        "touch-y": ["touch"],
        "touch-pz": ["touch"],
      },
      conflictingClassGroupModifiers: { "font-size": ["leading"] },
    };
  },
  Hw = _w($w);
function Or(...e) {
  return Hw(cw(e));
}
function jw(e) {
  const t = new Date(e),
    r = new Date().getTime() - t.getTime();
  return r < 6e4
    ? "刚刚"
    : r < 36e5
      ? `${Math.floor(r / 6e4)}分钟前`
      : r < 864e5
        ? `${Math.floor(r / 36e5)}小时前`
        : t.toLocaleDateString("zh-CN");
}
function Ww({
  mode = "chat",
  sessions = [],
  activeId,
  onSelect,
  onCreate,
  onDelete,
  workView = "rag",
  onWorkView,
}) {
  const e = tc();
  const toggle = (m) => (m === "chat" ? e("/") : m === "work" ? e("/work") : m === "digest" ? e("/digest") : e("/papers"));
  const workItems = [
    { key: "rag", label: "标准检索", icon: WkSearch },
    { key: "upload", label: "文件上传", icon: WkUpload },
    { key: "homework", label: "习题解答", icon: nw },
  ];
  const body =
    mode === "chat"
      ? [
          T.jsx("div", {
            className: "px-3 pt-2 pb-2",
            children: T.jsxs("button", {
              onClick: onCreate,
              className:
                "w-full flex items-center gap-2 px-3 py-2.5 rounded-2xl bg-accent hover:bg-orange-200 text-accent-foreground text-sm font-medium transition-all duration-200",
              children: [T.jsx(ow, { className: "w-4 h-4" }), "New Chat"],
            }),
          }),
          T.jsxs("div", {
            className: "flex-1 overflow-y-auto px-2",
            children: [
              sessions.length === 0 &&
                T.jsx("p", {
                  className:
                    "text-muted-foreground/40 text-xs text-center mt-12 leading-relaxed",
                  children: "No conversations yet.",
                }),
              sessions.map((o) => {
                const l = o.id === activeId;
                return T.jsxs(
                  "div",
                  {
                    onClick: () => onSelect(o.id),
                    className: Or(
                      "flex items-center gap-2.5 px-3 py-2.5 mb-1 cursor-pointer group rounded-2xl transition-all duration-200",
                      l
                        ? "bg-white shadow-sm border border-cream-200"
                        : "hover:bg-white/60 border border-transparent",
                    ),
                    children: [
                      T.jsx(rw, {
                        className: Or(
                          "w-4 h-4 shrink-0",
                          l ? "text-sunset-500" : "text-muted-foreground/40",
                        ),
                      }),
                      T.jsxs("div", {
                        className: "flex-1 min-w-0",
                        children: [
                          T.jsx("p", {
                            className: Or(
                              "text-sm truncate font-medium",
                              l ? "text-foreground" : "text-muted-foreground",
                            ),
                            children: o.title,
                          }),
                          T.jsx("p", {
                            className: "text-xs text-muted-foreground/50",
                            children: jw(o.updated_at),
                          }),
                        ],
                      }),
                      T.jsx("button", {
                        onClick: (a) => {
                          a.stopPropagation();
                          onDelete(o.id);
                        },
                        className:
                          "p-1 rounded-lg opacity-0 group-hover:opacity-100 hover:bg-red-50 transition-all text-muted-foreground/40 hover:text-red-400",
                        children: T.jsx(aw, { className: "w-3.5 h-3.5" }),
                      }),
                    ],
                  },
                  o.id,
                );
              }),
            ],
          }),
        ]
      : mode === "work"
        ? [
          T.jsxs("div", {
            className: "flex-1 overflow-y-auto px-2 pt-2",
            children: workItems.map((it) => {
              const Icon = it.icon;
              const active = workView === it.key;
              return T.jsxs(
                "button",
                {
                  key: it.key,
                  onClick: () => onWorkView(it.key),
                  className: Or(
                    "w-full flex items-center gap-2.5 px-3 py-2.5 mb-1 cursor-pointer rounded-2xl transition-all duration-200",
                    active
                      ? "bg-white shadow-sm border border-cream-200"
                      : "hover:bg-white/60 border border-transparent",
                  ),
                  children: [
                    T.jsx(Icon, {
                      className: Or(
                        "w-4 h-4 shrink-0",
                        active ? "text-sunset-500" : "text-muted-foreground/40",
                      ),
                    }),
                    T.jsx("span", {
                      className: Or(
                        "text-sm font-medium",
                        active ? "text-foreground" : "text-muted-foreground",
                      ),
                      children: it.label,
                    }),
                  ],
                },
                it.key,
              );
            }),
          }),
        ]
        : [];
  return T.jsxs("aside", {
    className:
      "w-64 flex flex-col h-full shrink-0 bg-gradient-to-b from-white via-white to-cream-50 border-r border-cream-200",
    children: [
      T.jsxs("div", {
        className: "p-4 border-b border-cream-200",
        children: [
          T.jsxs("div", {
            className: "flex items-center gap-2.5 mb-1",
            children: [
              T.jsx("div", {
                className:
                  "w-8 h-8 rounded-xl bg-gradient-to-br from-sunset-400 to-lavender-500 flex items-center justify-center shadow-sm",
                children: T.jsx(xl, { className: "w-4.5 h-4.5 text-white" }),
              }),
              T.jsx("span", {
                className: "font-brand text-lg text-foreground",
                children: "WAgent",
              }),
            ],
          }),
          T.jsx("p", {
            className: "text-xs text-muted-foreground/60 pl-10",
            children: "Wireless AI Assistant",
          }),
        ],
      }),
      T.jsx("div", {
        className: "px-3 pt-3 pb-2",
        children: T.jsxs("div", {
          className:
            "grid gap-1 p-1 rounded-2xl bg-cream-100 border border-cream-200",
          style: { gridTemplateColumns: "repeat(4, minmax(0, 1fr))" },
          children: [
            T.jsxs("button", {
              onClick: () => toggle("chat"),
              className: Or(
                "flex items-center justify-center gap-1.5 py-2 rounded-xl text-sm font-medium transition-all duration-200",
                mode === "chat"
                  ? "bg-white shadow-sm text-sunset-600"
                  : "text-muted-foreground hover:text-foreground",
              ),
              children: [T.jsx(rw, { className: "w-4 h-4" }), "对话"],
            }),
            T.jsxs("button", {
              onClick: () => toggle("work"),
              className: Or(
                "flex items-center justify-center gap-1.5 py-2 rounded-xl text-sm font-medium transition-all duration-200",
                mode === "work"
                  ? "bg-white shadow-sm text-sunset-600"
                  : "text-muted-foreground hover:text-foreground",
              ),
              children: [T.jsx(WkBriefcase, { className: "w-4 h-4" }), "工作"],
            }),
            T.jsxs("button", {
              onClick: () => toggle("digest"),
              className: Or(
                "flex items-center justify-center gap-1.5 py-2 rounded-xl text-sm font-medium transition-all duration-200",
                mode === "digest"
                  ? "bg-white shadow-sm text-sunset-600"
                  : "text-muted-foreground hover:text-foreground",
              ),
              children: [T.jsx(WkPaper, { className: "w-4 h-4" }), "速递"],
            }),
            T.jsxs("button", {
              onClick: () => toggle("papers"),
              className: Or(
                "flex items-center justify-center gap-1.5 py-2 rounded-xl text-sm font-medium transition-all duration-200",
                mode === "papers"
                  ? "bg-white shadow-sm text-sunset-600"
                  : "text-muted-foreground hover:text-foreground",
              ),
              children: [T.jsx(nw, { className: "w-4 h-4" }), "答疑"],
            }),
          ],
        }),
      }),
      ...body,
      T.jsxs("div", {
        className: "p-3 border-t border-cream-200 space-y-2",
        children: [
          T.jsx("a", {
            href: "/login",
            className:
              "block text-center text-xs text-muted-foreground/40 hover:text-sunset-500 transition-colors",
            children: "Login / Register",
          }),
          T.jsx("p", {
            className: "text-xs text-muted-foreground/30 text-center",
            children: "Powered by OpenClaw",
          }),
        ],
      }),
    ],
  });
}
function Gw(e, t) {
  const n = {};
  return (e[e.length - 1] === "" ? [...e, ""] : e)
    .join((n.padRight ? " " : "") + "," + (n.padLeft === !1 ? "" : " "))
    .trim();
}
const Kw = /^[$_\p{ID_Start}][$_\u{200C}\u{200D}\p{ID_Continue}]*$/u,
  Vw = /^[$_\p{ID_Start}][-$_\u{200C}\u{200D}\p{ID_Continue}]*$/u,
  qw = {};
function Yd(e, t) {
  return (qw.jsx ? Vw : Kw).test(e);
}
const Yw = /[ \t\n\f\r]/g;
function Qw(e) {
  return typeof e == "object" ? (e.type === "text" ? Qd(e.value) : !1) : Qd(e);
}
function Qd(e) {
  return e.replace(Yw, "") === "";
}
class io {
  constructor(t, n, r) {
    ((this.normal = n), (this.property = t), r && (this.space = r));
  }
}
io.prototype.normal = {};
io.prototype.property = {};
io.prototype.space = void 0;
function Wg(e, t) {
  const n = {},
    r = {};
  for (const i of e) (Object.assign(n, i.property), Object.assign(r, i.normal));
  return new io(n, r, t);
}
function Gs(e) {
  return e.toLowerCase();
}
class nt {
  constructor(t, n) {
    ((this.attribute = n), (this.property = t));
  }
}
nt.prototype.attribute = "";
nt.prototype.booleanish = !1;
nt.prototype.boolean = !1;
nt.prototype.commaOrSpaceSeparated = !1;
nt.prototype.commaSeparated = !1;
nt.prototype.defined = !1;
nt.prototype.mustUseProperty = !1;
nt.prototype.number = !1;
nt.prototype.overloadedBoolean = !1;
nt.prototype.property = "";
nt.prototype.spaceSeparated = !1;
nt.prototype.space = void 0;
let Zw = 0;
const Z = tr(),
  Se = tr(),
  Ks = tr(),
  z = tr(),
  ce = tr(),
  Wn = tr(),
  it = tr();
function tr() {
  return 2 ** ++Zw;
}
const Vs = Object.freeze(
    Object.defineProperty(
      {
        __proto__: null,
        boolean: Z,
        booleanish: Se,
        commaOrSpaceSeparated: it,
        commaSeparated: Wn,
        number: z,
        overloadedBoolean: Ks,
        spaceSeparated: ce,
      },
      Symbol.toStringTag,
      { value: "Module" },
    ),
  ),
  Aa = Object.keys(Vs);
class ic extends nt {
  constructor(t, n, r, i) {
    let o = -1;
    if ((super(t, n), Zd(this, "space", i), typeof r == "number"))
      for (; ++o < Aa.length;) {
        const l = Aa[o];
        Zd(this, Aa[o], (r & Vs[l]) === Vs[l]);
      }
  }
}
ic.prototype.defined = !0;
function Zd(e, t, n) {
  n && (e[t] = n);
}
function Kr(e) {
  const t = {},
    n = {};
  for (const [r, i] of Object.entries(e.properties)) {
    const o = new ic(r, e.transform(e.attributes || {}, r), i, e.space);
    (e.mustUseProperty &&
      e.mustUseProperty.includes(r) &&
      (o.mustUseProperty = !0),
      (t[r] = o),
      (n[Gs(r)] = r),
      (n[Gs(o.attribute)] = r));
  }
  return new io(t, n, e.space);
}
const Gg = Kr({
  properties: {
    ariaActiveDescendant: null,
    ariaAtomic: Se,
    ariaAutoComplete: null,
    ariaBusy: Se,
    ariaChecked: Se,
    ariaColCount: z,
    ariaColIndex: z,
    ariaColSpan: z,
    ariaControls: ce,
    ariaCurrent: null,
    ariaDescribedBy: ce,
    ariaDetails: null,
    ariaDisabled: Se,
    ariaDropEffect: ce,
    ariaErrorMessage: null,
    ariaExpanded: Se,
    ariaFlowTo: ce,
    ariaGrabbed: Se,
    ariaHasPopup: null,
    ariaHidden: Se,
    ariaInvalid: null,
    ariaKeyShortcuts: null,
    ariaLabel: null,
    ariaLabelledBy: ce,
    ariaLevel: z,
    ariaLive: null,
    ariaModal: Se,
    ariaMultiLine: Se,
    ariaMultiSelectable: Se,
    ariaOrientation: null,
    ariaOwns: ce,
    ariaPlaceholder: null,
    ariaPosInSet: z,
    ariaPressed: Se,
    ariaReadOnly: Se,
    ariaRelevant: null,
    ariaRequired: Se,
    ariaRoleDescription: ce,
    ariaRowCount: z,
    ariaRowIndex: z,
    ariaRowSpan: z,
    ariaSelected: Se,
    ariaSetSize: z,
    ariaSort: null,
    ariaValueMax: z,
    ariaValueMin: z,
    ariaValueNow: z,
    ariaValueText: null,
    role: null,
  },
  transform(e, t) {
    return t === "role" ? t : "aria-" + t.slice(4).toLowerCase();
  },
});
function Kg(e, t) {
  return t in e ? e[t] : t;
}
function Vg(e, t) {
  return Kg(e, t.toLowerCase());
}
const Xw = Kr({
    attributes: {
      acceptcharset: "accept-charset",
      classname: "class",
      htmlfor: "for",
      httpequiv: "http-equiv",
    },
    mustUseProperty: ["checked", "multiple", "muted", "selected"],
    properties: {
      abbr: null,
      accept: Wn,
      acceptCharset: ce,
      accessKey: ce,
      action: null,
      allow: null,
      allowFullScreen: Z,
      allowPaymentRequest: Z,
      allowUserMedia: Z,
      alpha: Z,
      alt: null,
      as: null,
      async: Z,
      autoCapitalize: null,
      autoComplete: ce,
      autoFocus: Z,
      autoPlay: Z,
      blocking: ce,
      capture: null,
      charSet: null,
      checked: Z,
      cite: null,
      className: ce,
      closedBy: null,
      colorSpace: null,
      cols: z,
      colSpan: z,
      command: null,
      commandFor: null,
      content: null,
      contentEditable: Se,
      controls: Z,
      controlsList: ce,
      coords: z | Wn,
      crossOrigin: null,
      data: null,
      dateTime: null,
      decoding: null,
      default: Z,
      defer: Z,
      dir: null,
      dirName: null,
      disabled: Z,
      download: Ks,
      draggable: Se,
      encType: null,
      enterKeyHint: null,
      fetchPriority: null,
      form: null,
      formAction: null,
      formEncType: null,
      formMethod: null,
      formNoValidate: Z,
      formTarget: null,
      headers: ce,
      height: z,
      hidden: Ks,
      high: z,
      href: null,
      hrefLang: null,
      htmlFor: ce,
      httpEquiv: ce,
      id: null,
      imageSizes: null,
      imageSrcSet: null,
      inert: Z,
      inputMode: null,
      integrity: null,
      is: null,
      isMap: Z,
      itemId: null,
      itemProp: ce,
      itemRef: ce,
      itemScope: Z,
      itemType: ce,
      kind: null,
      label: null,
      lang: null,
      language: null,
      list: null,
      loading: null,
      loop: Z,
      low: z,
      manifest: null,
      max: null,
      maxLength: z,
      media: null,
      method: null,
      min: null,
      minLength: z,
      multiple: Z,
      muted: Z,
      name: null,
      nonce: null,
      noModule: Z,
      noValidate: Z,
      onAbort: null,
      onAfterPrint: null,
      onAuxClick: null,
      onBeforeMatch: null,
      onBeforePrint: null,
      onBeforeToggle: null,
      onBeforeUnload: null,
      onBlur: null,
      onCancel: null,
      onCanPlay: null,
      onCanPlayThrough: null,
      onChange: null,
      onClick: null,
      onClose: null,
      onContextLost: null,
      onContextMenu: null,
      onContextRestored: null,
      onCopy: null,
      onCueChange: null,
      onCut: null,
      onDblClick: null,
      onDrag: null,
      onDragEnd: null,
      onDragEnter: null,
      onDragExit: null,
      onDragLeave: null,
      onDragOver: null,
      onDragStart: null,
      onDrop: null,
      onDurationChange: null,
      onEmptied: null,
      onEnded: null,
      onError: null,
      onFocus: null,
      onFormData: null,
      onHashChange: null,
      onInput: null,
      onInvalid: null,
      onKeyDown: null,
      onKeyPress: null,
      onKeyUp: null,
      onLanguageChange: null,
      onLoad: null,
      onLoadedData: null,
      onLoadedMetadata: null,
      onLoadEnd: null,
      onLoadStart: null,
      onMessage: null,
      onMessageError: null,
      onMouseDown: null,
      onMouseEnter: null,
      onMouseLeave: null,
      onMouseMove: null,
      onMouseOut: null,
      onMouseOver: null,
      onMouseUp: null,
      onOffline: null,
      onOnline: null,
      onPageHide: null,
      onPageShow: null,
      onPaste: null,
      onPause: null,
      onPlay: null,
      onPlaying: null,
      onPopState: null,
      onProgress: null,
      onRateChange: null,
      onRejectionHandled: null,
      onReset: null,
      onResize: null,
      onScroll: null,
      onScrollEnd: null,
      onSecurityPolicyViolation: null,
      onSeeked: null,
      onSeeking: null,
      onSelect: null,
      onSlotChange: null,
      onStalled: null,
      onStorage: null,
      onSubmit: null,
      onSuspend: null,
      onTimeUpdate: null,
      onToggle: null,
      onUnhandledRejection: null,
      onUnload: null,
      onVolumeChange: null,
      onWaiting: null,
      onWheel: null,
      open: Z,
      optimum: z,
      pattern: null,
      ping: ce,
      placeholder: null,
      playsInline: Z,
      popover: null,
      popoverTarget: null,
      popoverTargetAction: null,
      poster: null,
      preload: null,
      readOnly: Z,
      referrerPolicy: null,
      rel: ce,
      required: Z,
      reversed: Z,
      rows: z,
      rowSpan: z,
      sandbox: ce,
      scope: null,
      scoped: Z,
      seamless: Z,
      selected: Z,
      shadowRootClonable: Z,
      shadowRootCustomElementRegistry: Z,
      shadowRootDelegatesFocus: Z,
      shadowRootMode: null,
      shadowRootSerializable: Z,
      shape: null,
      size: z,
      sizes: null,
      slot: null,
      span: z,
      spellCheck: Se,
      src: null,
      srcDoc: null,
      srcLang: null,
      srcSet: null,
      start: z,
      step: null,
      style: null,
      tabIndex: z,
      target: null,
      title: null,
      translate: null,
      type: null,
      typeMustMatch: Z,
      useMap: null,
      value: Se,
      width: z,
      wrap: null,
      writingSuggestions: null,
      align: null,
      aLink: null,
      archive: ce,
      axis: null,
      background: null,
      bgColor: null,
      border: z,
      borderColor: null,
      bottomMargin: z,
      cellPadding: null,
      cellSpacing: null,
      char: null,
      charOff: null,
      classId: null,
      clear: null,
      code: null,
      codeBase: null,
      codeType: null,
      color: null,
      compact: Z,
      declare: Z,
      event: null,
      face: null,
      frame: null,
      frameBorder: null,
      hSpace: z,
      leftMargin: z,
      link: null,
      longDesc: null,
      lowSrc: null,
      marginHeight: z,
      marginWidth: z,
      noResize: Z,
      noHref: Z,
      noShade: Z,
      noWrap: Z,
      object: null,
      profile: null,
      prompt: null,
      rev: null,
      rightMargin: z,
      rules: null,
      scheme: null,
      scrolling: Se,
      standby: null,
      summary: null,
      text: null,
      topMargin: z,
      valueType: null,
      version: null,
      vAlign: null,
      vLink: null,
      vSpace: z,
      allowTransparency: null,
      autoCorrect: null,
      autoSave: null,
      credentialless: Z,
      disablePictureInPicture: Z,
      disableRemotePlayback: Z,
      exportParts: Wn,
      part: ce,
      prefix: null,
      property: null,
      results: z,
      security: null,
      unselectable: null,
    },
    space: "html",
    transform: Vg,
  }),
  Jw = Kr({
    attributes: {
      accentHeight: "accent-height",
      alignmentBaseline: "alignment-baseline",
      arabicForm: "arabic-form",
      baselineShift: "baseline-shift",
      capHeight: "cap-height",
      className: "class",
      clipPath: "clip-path",
      clipRule: "clip-rule",
      colorInterpolation: "color-interpolation",
      colorInterpolationFilters: "color-interpolation-filters",
      colorProfile: "color-profile",
      colorRendering: "color-rendering",
      crossOrigin: "crossorigin",
      dataType: "datatype",
      dominantBaseline: "dominant-baseline",
      enableBackground: "enable-background",
      fillOpacity: "fill-opacity",
      fillRule: "fill-rule",
      floodColor: "flood-color",
      floodOpacity: "flood-opacity",
      fontFamily: "font-family",
      fontSize: "font-size",
      fontSizeAdjust: "font-size-adjust",
      fontStretch: "font-stretch",
      fontStyle: "font-style",
      fontVariant: "font-variant",
      fontWeight: "font-weight",
      glyphName: "glyph-name",
      glyphOrientationHorizontal: "glyph-orientation-horizontal",
      glyphOrientationVertical: "glyph-orientation-vertical",
      hrefLang: "hreflang",
      horizAdvX: "horiz-adv-x",
      horizOriginX: "horiz-origin-x",
      horizOriginY: "horiz-origin-y",
      imageRendering: "image-rendering",
      letterSpacing: "letter-spacing",
      lightingColor: "lighting-color",
      markerEnd: "marker-end",
      markerMid: "marker-mid",
      markerStart: "marker-start",
      maskType: "mask-type",
      navDown: "nav-down",
      navDownLeft: "nav-down-left",
      navDownRight: "nav-down-right",
      navLeft: "nav-left",
      navNext: "nav-next",
      navPrev: "nav-prev",
      navRight: "nav-right",
      navUp: "nav-up",
      navUpLeft: "nav-up-left",
      navUpRight: "nav-up-right",
      onAbort: "onabort",
      onActivate: "onactivate",
      onAfterPrint: "onafterprint",
      onBeforePrint: "onbeforeprint",
      onBegin: "onbegin",
      onCancel: "oncancel",
      onCanPlay: "oncanplay",
      onCanPlayThrough: "oncanplaythrough",
      onChange: "onchange",
      onClick: "onclick",
      onClose: "onclose",
      onCopy: "oncopy",
      onCueChange: "oncuechange",
      onCut: "oncut",
      onDblClick: "ondblclick",
      onDrag: "ondrag",
      onDragEnd: "ondragend",
      onDragEnter: "ondragenter",
      onDragExit: "ondragexit",
      onDragLeave: "ondragleave",
      onDragOver: "ondragover",
      onDragStart: "ondragstart",
      onDrop: "ondrop",
      onDurationChange: "ondurationchange",
      onEmptied: "onemptied",
      onEnd: "onend",
      onEnded: "onended",
      onError: "onerror",
      onFocus: "onfocus",
      onFocusIn: "onfocusin",
      onFocusOut: "onfocusout",
      onHashChange: "onhashchange",
      onInput: "oninput",
      onInvalid: "oninvalid",
      onKeyDown: "onkeydown",
      onKeyPress: "onkeypress",
      onKeyUp: "onkeyup",
      onLoad: "onload",
      onLoadedData: "onloadeddata",
      onLoadedMetadata: "onloadedmetadata",
      onLoadStart: "onloadstart",
      onMessage: "onmessage",
      onMouseDown: "onmousedown",
      onMouseEnter: "onmouseenter",
      onMouseLeave: "onmouseleave",
      onMouseMove: "onmousemove",
      onMouseOut: "onmouseout",
      onMouseOver: "onmouseover",
      onMouseUp: "onmouseup",
      onMouseWheel: "onmousewheel",
      onOffline: "onoffline",
      onOnline: "ononline",
      onPageHide: "onpagehide",
      onPageShow: "onpageshow",
      onPaste: "onpaste",
      onPause: "onpause",
      onPlay: "onplay",
      onPlaying: "onplaying",
      onPopState: "onpopstate",
      onProgress: "onprogress",
      onRateChange: "onratechange",
      onRepeat: "onrepeat",
      onReset: "onreset",
      onResize: "onresize",
      onScroll: "onscroll",
      onSeeked: "onseeked",
      onSeeking: "onseeking",
      onSelect: "onselect",
      onShow: "onshow",
      onStalled: "onstalled",
      onStorage: "onstorage",
      onSubmit: "onsubmit",
      onSuspend: "onsuspend",
      onTimeUpdate: "ontimeupdate",
      onToggle: "ontoggle",
      onUnload: "onunload",
      onVolumeChange: "onvolumechange",
      onWaiting: "onwaiting",
      onZoom: "onzoom",
      overlinePosition: "overline-position",
      overlineThickness: "overline-thickness",
      paintOrder: "paint-order",
      panose1: "panose-1",
      pointerEvents: "pointer-events",
      referrerPolicy: "referrerpolicy",
      renderingIntent: "rendering-intent",
      shapeRendering: "shape-rendering",
      stopColor: "stop-color",
      stopOpacity: "stop-opacity",
      strikethroughPosition: "strikethrough-position",
      strikethroughThickness: "strikethrough-thickness",
      strokeDashArray: "stroke-dasharray",
      strokeDashOffset: "stroke-dashoffset",
      strokeLineCap: "stroke-linecap",
      strokeLineJoin: "stroke-linejoin",
      strokeMiterLimit: "stroke-miterlimit",
      strokeOpacity: "stroke-opacity",
      strokeWidth: "stroke-width",
      tabIndex: "tabindex",
      textAnchor: "text-anchor",
      textDecoration: "text-decoration",
      textRendering: "text-rendering",
      transformOrigin: "transform-origin",
      typeOf: "typeof",
      underlinePosition: "underline-position",
      underlineThickness: "underline-thickness",
      unicodeBidi: "unicode-bidi",
      unicodeRange: "unicode-range",
      unitsPerEm: "units-per-em",
      vAlphabetic: "v-alphabetic",
      vHanging: "v-hanging",
      vIdeographic: "v-ideographic",
      vMathematical: "v-mathematical",
      vectorEffect: "vector-effect",
      vertAdvY: "vert-adv-y",
      vertOriginX: "vert-origin-x",
      vertOriginY: "vert-origin-y",
      wordSpacing: "word-spacing",
      writingMode: "writing-mode",
      xHeight: "x-height",
      playbackOrder: "playbackorder",
      timelineBegin: "timelinebegin",
    },
    properties: {
      about: it,
      accentHeight: z,
      accumulate: null,
      additive: null,
      alignmentBaseline: null,
      alphabetic: z,
      amplitude: z,
      arabicForm: null,
      ascent: z,
      attributeName: null,
      attributeType: null,
      azimuth: z,
      bandwidth: null,
      baselineShift: null,
      baseFrequency: null,
      baseProfile: null,
      bbox: null,
      begin: null,
      bias: z,
      by: null,
      calcMode: null,
      capHeight: z,
      className: ce,
      clip: null,
      clipPath: null,
      clipPathUnits: null,
      clipRule: null,
      color: null,
      colorInterpolation: null,
      colorInterpolationFilters: null,
      colorProfile: null,
      colorRendering: null,
      content: null,
      contentScriptType: null,
      contentStyleType: null,
      crossOrigin: null,
      cursor: null,
      cx: null,
      cy: null,
      d: null,
      dataType: null,
      defaultAction: null,
      descent: z,
      diffuseConstant: z,
      direction: null,
      display: null,
      dur: null,
      divisor: z,
      dominantBaseline: null,
      download: Z,
      dx: null,
      dy: null,
      edgeMode: null,
      editable: null,
      elevation: z,
      enableBackground: null,
      end: null,
      event: null,
      exponent: z,
      externalResourcesRequired: null,
      fill: null,
      fillOpacity: z,
      fillRule: null,
      filter: null,
      filterRes: null,
      filterUnits: null,
      floodColor: null,
      floodOpacity: null,
      focusable: null,
      focusHighlight: null,
      fontFamily: null,
      fontSize: null,
      fontSizeAdjust: null,
      fontStretch: null,
      fontStyle: null,
      fontVariant: null,
      fontWeight: null,
      format: null,
      fr: null,
      from: null,
      fx: null,
      fy: null,
      g1: Wn,
      g2: Wn,
      glyphName: Wn,
      glyphOrientationHorizontal: null,
      glyphOrientationVertical: null,
      glyphRef: null,
      gradientTransform: null,
      gradientUnits: null,
      handler: null,
      hanging: z,
      hatchContentUnits: null,
      hatchUnits: null,
      height: null,
      href: null,
      hrefLang: null,
      horizAdvX: z,
      horizOriginX: z,
      horizOriginY: z,
      id: null,
      ideographic: z,
      imageRendering: null,
      initialVisibility: null,
      in: null,
      in2: null,
      intercept: z,
      k: z,
      k1: z,
      k2: z,
      k3: z,
      k4: z,
      kernelMatrix: it,
      kernelUnitLength: null,
      keyPoints: null,
      keySplines: null,
      keyTimes: null,
      kerning: null,
      lang: null,
      lengthAdjust: null,
      letterSpacing: null,
      lightingColor: null,
      limitingConeAngle: z,
      local: null,
      markerEnd: null,
      markerMid: null,
      markerStart: null,
      markerHeight: null,
      markerUnits: null,
      markerWidth: null,
      mask: null,
      maskContentUnits: null,
      maskType: null,
      maskUnits: null,
      mathematical: null,
      max: null,
      media: null,
      mediaCharacterEncoding: null,
      mediaContentEncodings: null,
      mediaSize: z,
      mediaTime: null,
      method: null,
      min: null,
      mode: null,
      name: null,
      navDown: null,
      navDownLeft: null,
      navDownRight: null,
      navLeft: null,
      navNext: null,
      navPrev: null,
      navRight: null,
      navUp: null,
      navUpLeft: null,
      navUpRight: null,
      numOctaves: null,
      observer: null,
      offset: null,
      onAbort: null,
      onActivate: null,
      onAfterPrint: null,
      onBeforePrint: null,
      onBegin: null,
      onCancel: null,
      onCanPlay: null,
      onCanPlayThrough: null,
      onChange: null,
      onClick: null,
      onClose: null,
      onCopy: null,
      onCueChange: null,
      onCut: null,
      onDblClick: null,
      onDrag: null,
      onDragEnd: null,
      onDragEnter: null,
      onDragExit: null,
      onDragLeave: null,
      onDragOver: null,
      onDragStart: null,
      onDrop: null,
      onDurationChange: null,
      onEmptied: null,
      onEnd: null,
      onEnded: null,
      onError: null,
      onFocus: null,
      onFocusIn: null,
      onFocusOut: null,
      onHashChange: null,
      onInput: null,
      onInvalid: null,
      onKeyDown: null,
      onKeyPress: null,
      onKeyUp: null,
      onLoad: null,
      onLoadedData: null,
      onLoadedMetadata: null,
      onLoadStart: null,
      onMessage: null,
      onMouseDown: null,
      onMouseEnter: null,
      onMouseLeave: null,
      onMouseMove: null,
      onMouseOut: null,
      onMouseOver: null,
      onMouseUp: null,
      onMouseWheel: null,
      onOffline: null,
      onOnline: null,
      onPageHide: null,
      onPageShow: null,
      onPaste: null,
      onPause: null,
      onPlay: null,
      onPlaying: null,
      onPopState: null,
      onProgress: null,
      onRateChange: null,
      onRepeat: null,
      onReset: null,
      onResize: null,
      onScroll: null,
      onSeeked: null,
      onSeeking: null,
      onSelect: null,
      onShow: null,
      onStalled: null,
      onStorage: null,
      onSubmit: null,
      onSuspend: null,
      onTimeUpdate: null,
      onToggle: null,
      onUnload: null,
      onVolumeChange: null,
      onWaiting: null,
      onZoom: null,
      opacity: null,
      operator: null,
      order: null,
      orient: null,
      orientation: null,
      origin: null,
      overflow: null,
      overlay: null,
      overlinePosition: z,
      overlineThickness: z,
      paintOrder: null,
      panose1: null,
      path: null,
      pathLength: z,
      patternContentUnits: null,
      patternTransform: null,
      patternUnits: null,
      phase: null,
      ping: ce,
      pitch: null,
      playbackOrder: null,
      pointerEvents: null,
      points: null,
      pointsAtX: z,
      pointsAtY: z,
      pointsAtZ: z,
      preserveAlpha: null,
      preserveAspectRatio: null,
      primitiveUnits: null,
      propagate: null,
      property: it,
      r: null,
      radius: null,
      referrerPolicy: null,
      refX: null,
      refY: null,
      rel: it,
      rev: it,
      renderingIntent: null,
      repeatCount: null,
      repeatDur: null,
      requiredExtensions: it,
      requiredFeatures: it,
      requiredFonts: it,
      requiredFormats: it,
      resource: null,
      restart: null,
      result: null,
      rotate: null,
      rx: null,
      ry: null,
      scale: null,
      seed: null,
      shapeRendering: null,
      side: null,
      slope: null,
      snapshotTime: null,
      specularConstant: z,
      specularExponent: z,
      spreadMethod: null,
      spacing: null,
      startOffset: null,
      stdDeviation: null,
      stemh: null,
      stemv: null,
      stitchTiles: null,
      stopColor: null,
      stopOpacity: null,
      strikethroughPosition: z,
      strikethroughThickness: z,
      string: null,
      stroke: null,
      strokeDashArray: it,
      strokeDashOffset: null,
      strokeLineCap: null,
      strokeLineJoin: null,
      strokeMiterLimit: z,
      strokeOpacity: z,
      strokeWidth: null,
      style: null,
      surfaceScale: z,
      syncBehavior: null,
      syncBehaviorDefault: null,
      syncMaster: null,
      syncTolerance: null,
      syncToleranceDefault: null,
      systemLanguage: it,
      tabIndex: z,
      tableValues: null,
      target: null,
      targetX: z,
      targetY: z,
      textAnchor: null,
      textDecoration: null,
      textRendering: null,
      textLength: null,
      timelineBegin: null,
      title: null,
      transformBehavior: null,
      type: null,
      typeOf: it,
      to: null,
      transform: null,
      transformOrigin: null,
      u1: null,
      u2: null,
      underlinePosition: z,
      underlineThickness: z,
      unicode: null,
      unicodeBidi: null,
      unicodeRange: null,
      unitsPerEm: z,
      values: null,
      vAlphabetic: z,
      vMathematical: z,
      vectorEffect: null,
      vHanging: z,
      vIdeographic: z,
      version: null,
      vertAdvY: z,
      vertOriginX: z,
      vertOriginY: z,
      viewBox: null,
      viewTarget: null,
      visibility: null,
      width: null,
      widths: null,
      wordSpacing: null,
      writingMode: null,
      x: null,
      x1: null,
      x2: null,
      xChannelSelector: null,
      xHeight: z,
      y: null,
      y1: null,
      y2: null,
      yChannelSelector: null,
      z: null,
      zoomAndPan: null,
    },
    space: "svg",
    transform: Kg,
  }),
  qg = Kr({
    properties: {
      xLinkActuate: null,
      xLinkArcRole: null,
      xLinkHref: null,
      xLinkRole: null,
      xLinkShow: null,
      xLinkTitle: null,
      xLinkType: null,
    },
    space: "xlink",
    transform(e, t) {
      return "xlink:" + t.slice(5).toLowerCase();
    },
  }),
  Yg = Kr({
    attributes: { xmlnsxlink: "xmlns:xlink" },
    properties: { xmlnsXLink: null, xmlns: null },
    space: "xmlns",
    transform: Vg,
  }),
  Qg = Kr({
    properties: { xmlBase: null, xmlLang: null, xmlSpace: null },
    space: "xml",
    transform(e, t) {
      return "xml:" + t.slice(3).toLowerCase();
    },
  }),
  ex = {
    classId: "classID",
    dataType: "datatype",
    itemId: "itemID",
    strokeDashArray: "strokeDasharray",
    strokeDashOffset: "strokeDashoffset",
    strokeLineCap: "strokeLinecap",
    strokeLineJoin: "strokeLinejoin",
    strokeMiterLimit: "strokeMiterlimit",
    typeOf: "typeof",
    xLinkActuate: "xlinkActuate",
    xLinkArcRole: "xlinkArcrole",
    xLinkHref: "xlinkHref",
    xLinkRole: "xlinkRole",
    xLinkShow: "xlinkShow",
    xLinkTitle: "xlinkTitle",
    xLinkType: "xlinkType",
    xmlnsXLink: "xmlnsXlink",
  },
  tx = /[A-Z]/g,
  Xd = /-[a-z]/g,
  nx = /^data[-\w.:]+$/i;
function rx(e, t) {
  const n = Gs(t);
  let r = t,
    i = nt;
  if (n in e.normal) return e.property[e.normal[n]];
  if (n.length > 4 && n.slice(0, 4) === "data" && nx.test(t)) {
    if (t.charAt(4) === "-") {
      const o = t.slice(5).replace(Xd, ox);
      r = "data" + o.charAt(0).toUpperCase() + o.slice(1);
    } else {
      const o = t.slice(4);
      if (!Xd.test(o)) {
        let l = o.replace(tx, ix);
        (l.charAt(0) !== "-" && (l = "-" + l), (t = "data" + l));
      }
    }
    i = ic;
  }
  return new i(r, t);
}
function ix(e) {
  return "-" + e.toLowerCase();
}
function ox(e) {
  return e.charAt(1).toUpperCase();
}
const lx = Wg([Gg, Xw, qg, Yg, Qg], "html"),
  oc = Wg([Gg, Jw, qg, Yg, Qg], "svg");
function ax(e) {
  return e.join(" ").trim();
}
var lc = {},
  Jd = /\/\*[^*]*\*+([^/*][^*]*\*+)*\//g,
  sx = /\n/g,
  ux = /^\s*/,
  cx = /^(\*?[-#/*\\\w]+(\[[0-9a-z_-]+\])?)\s*/,
  dx = /^:\s*/,
  fx = /^((?:'(?:\\'|.)*?'|"(?:\\"|.)*?"|\([^)]*?\)|[^};])+)/,
  px = /^[;\s]*/,
  hx = /^\s+|\s+$/g,
  gx = `
`,
  ef = "/",
  tf = "*",
  zn = "",
  mx = "comment",
  yx = "declaration";
function bx(e, t) {
  if (typeof e != "string")
    throw new TypeError("First argument must be a string");
  if (!e) return [];
  t = t || {};
  var n = 1,
    r = 1;
  function i(g) {
    var y = g.match(sx);
    y && (n += y.length);
    var E = g.lastIndexOf(gx);
    r = ~E ? g.length - E : r + g.length;
  }
  function o() {
    var g = { line: n, column: r };
    return function (y) {
      return ((y.position = new l(g)), u(), y);
    };
  }
  function l(g) {
    ((this.start = g),
      (this.end = { line: n, column: r }),
      (this.source = t.source));
  }
  l.prototype.content = e;
  function a(g) {
    var y = new Error(t.source + ":" + n + ":" + r + ": " + g);
    if (
      ((y.reason = g),
      (y.filename = t.source),
      (y.line = n),
      (y.column = r),
      (y.source = e),
      !t.silent)
    )
      throw y;
  }
  function s(g) {
    var y = g.exec(e);
    if (y) {
      var E = y[0];
      return (i(E), (e = e.slice(E.length)), y);
    }
  }
  function u() {
    s(ux);
  }
  function d(g) {
    var y;
    for (g = g || []; (y = c());) y !== !1 && g.push(y);
    return g;
  }
  function c() {
    var g = o();
    if (!(ef != e.charAt(0) || tf != e.charAt(1))) {
      for (
        var y = 2;
        zn != e.charAt(y) && (tf != e.charAt(y) || ef != e.charAt(y + 1));
      )
        ++y;
      if (((y += 2), zn === e.charAt(y - 1)))
        return a("End of comment missing");
      var E = e.slice(2, y - 2);
      return (
        (r += 2),
        i(E),
        (e = e.slice(y)),
        (r += 2),
        g({ type: mx, comment: E })
      );
    }
  }
  function f() {
    var g = o(),
      y = s(cx);
    if (y) {
      if ((c(), !s(dx))) return a("property missing ':'");
      var E = s(fx),
        h = g({
          type: yx,
          property: nf(y[0].replace(Jd, zn)),
          value: E ? nf(E[0].replace(Jd, zn)) : zn,
        });
      return (s(px), h);
    }
  }
  function p() {
    var g = [];
    d(g);
    for (var y; (y = f());) y !== !1 && (g.push(y), d(g));
    return g;
  }
  return (u(), p());
}
function nf(e) {
  return e ? e.replace(hx, zn) : zn;
}
var vx = bx,
  Ex =
    (Zo && Zo.__importDefault) ||
    function (e) {
      return e && e.__esModule ? e : { default: e };
    };
Object.defineProperty(lc, "__esModule", { value: !0 });
lc.default = xx;
const wx = Ex(vx);
function xx(e, t) {
  let n = null;
  if (!e || typeof e != "string") return n;
  const r = (0, wx.default)(e),
    i = typeof t == "function";
  return (
    r.forEach((o) => {
      if (o.type !== "declaration") return;
      const { property: l, value: a } = o;
      i ? t(l, a, o) : a && ((n = n || {}), (n[l] = a));
    }),
    n
  );
}
var ql = {};
Object.defineProperty(ql, "__esModule", { value: !0 });
ql.camelCase = void 0;
var _x = /^--[a-zA-Z0-9_-]+$/,
  kx = /-([a-z])/g,
  Sx = /^[^-]+$/,
  Nx = /^-(webkit|moz|ms|o|khtml)-/,
  Cx = /^-(ms)-/,
  Tx = function (e) {
    return !e || Sx.test(e) || _x.test(e);
  },
  Ax = function (e, t) {
    return t.toUpperCase();
  },
  rf = function (e, t) {
    return "".concat(t, "-");
  },
  Rx = function (e, t) {
    return (
      t === void 0 && (t = {}),
      Tx(e)
        ? e
        : ((e = e.toLowerCase()),
          t.reactCompat ? (e = e.replace(Cx, rf)) : (e = e.replace(Nx, rf)),
          e.replace(kx, Ax))
    );
  };
ql.camelCase = Rx;
var Ox =
    (Zo && Zo.__importDefault) ||
    function (e) {
      return e && e.__esModule ? e : { default: e };
    },
  Ix = Ox(lc),
  Mx = ql;
function qs(e, t) {
  var n = {};
  return (
    !e ||
      typeof e != "string" ||
      (0, Ix.default)(e, function (r, i) {
        r && i && (n[(0, Mx.camelCase)(r, t)] = i);
      }),
    n
  );
}
qs.default = qs;
var Lx = qs;
const Dx = Rl(Lx),
  Zg = Xg("end"),
  ac = Xg("start");
function Xg(e) {
  return t;
  function t(n) {
    const r = (n && n.position && n.position[e]) || {};
    if (
      typeof r.line == "number" &&
      r.line > 0 &&
      typeof r.column == "number" &&
      r.column > 0
    )
      return {
        line: r.line,
        column: r.column,
        offset:
          typeof r.offset == "number" && r.offset > -1 ? r.offset : void 0,
      };
  }
}
function Px(e) {
  const t = ac(e),
    n = Zg(e);
  if (t && n) return { start: t, end: n };
}
function Si(e) {
  return !e || typeof e != "object"
    ? ""
    : "position" in e || "type" in e
      ? of(e.position)
      : "start" in e || "end" in e
        ? of(e)
        : "line" in e || "column" in e
          ? Ys(e)
          : "";
}
function Ys(e) {
  return lf(e && e.line) + ":" + lf(e && e.column);
}
function of(e) {
  return Ys(e && e.start) + "-" + Ys(e && e.end);
}
function lf(e) {
  return e && typeof e == "number" ? e : 1;
}
class Ue extends Error {
  constructor(t, n, r) {
    (super(), typeof n == "string" && ((r = n), (n = void 0)));
    let i = "",
      o = {},
      l = !1;
    if (
      (n &&
        ("line" in n && "column" in n
          ? (o = { place: n })
          : "start" in n && "end" in n
            ? (o = { place: n })
            : "type" in n
              ? (o = { ancestors: [n], place: n.position })
              : (o = { ...n })),
      typeof t == "string"
        ? (i = t)
        : !o.cause && t && ((l = !0), (i = t.message), (o.cause = t)),
      !o.ruleId && !o.source && typeof r == "string")
    ) {
      const s = r.indexOf(":");
      s === -1
        ? (o.ruleId = r)
        : ((o.source = r.slice(0, s)), (o.ruleId = r.slice(s + 1)));
    }
    if (!o.place && o.ancestors && o.ancestors) {
      const s = o.ancestors[o.ancestors.length - 1];
      s && (o.place = s.position);
    }
    const a = o.place && "start" in o.place ? o.place.start : o.place;
    ((this.ancestors = o.ancestors || void 0),
      (this.cause = o.cause || void 0),
      (this.column = a ? a.column : void 0),
      (this.fatal = void 0),
      (this.file = ""),
      (this.message = i),
      (this.line = a ? a.line : void 0),
      (this.name = Si(o.place) || "1:1"),
      (this.place = o.place || void 0),
      (this.reason = this.message),
      (this.ruleId = o.ruleId || void 0),
      (this.source = o.source || void 0),
      (this.stack =
        l && o.cause && typeof o.cause.stack == "string" ? o.cause.stack : ""),
      (this.actual = void 0),
      (this.expected = void 0),
      (this.note = void 0),
      (this.url = void 0));
  }
}
Ue.prototype.file = "";
Ue.prototype.name = "";
Ue.prototype.reason = "";
Ue.prototype.message = "";
Ue.prototype.stack = "";
Ue.prototype.column = void 0;
Ue.prototype.line = void 0;
Ue.prototype.ancestors = void 0;
Ue.prototype.cause = void 0;
Ue.prototype.fatal = void 0;
Ue.prototype.place = void 0;
Ue.prototype.ruleId = void 0;
Ue.prototype.source = void 0;
const sc = {}.hasOwnProperty,
  zx = new Map(),
  Fx = /[A-Z]/g,
  Bx = new Set(["table", "tbody", "thead", "tfoot", "tr"]),
  Ux = new Set(["td", "th"]),
  Jg = "https://github.com/syntax-tree/hast-util-to-jsx-runtime";
function $x(e, t) {
  if (!t || t.Fragment === void 0)
    throw new TypeError("Expected `Fragment` in options");
  const n = t.filePath || void 0;
  let r;
  if (t.development) {
    if (typeof t.jsxDEV != "function")
      throw new TypeError(
        "Expected `jsxDEV` in options when `development: true`",
      );
    r = Yx(n, t.jsxDEV);
  } else {
    if (typeof t.jsx != "function")
      throw new TypeError("Expected `jsx` in production options");
    if (typeof t.jsxs != "function")
      throw new TypeError("Expected `jsxs` in production options");
    r = qx(n, t.jsx, t.jsxs);
  }
  const i = {
      Fragment: t.Fragment,
      ancestors: [],
      components: t.components || {},
      create: r,
      elementAttributeNameCase: t.elementAttributeNameCase || "react",
      evaluater: t.createEvaluater ? t.createEvaluater() : void 0,
      filePath: n,
      ignoreInvalidStyle: t.ignoreInvalidStyle || !1,
      passKeys: t.passKeys !== !1,
      passNode: t.passNode || !1,
      schema: t.space === "svg" ? oc : lx,
      stylePropertyNameCase: t.stylePropertyNameCase || "dom",
      tableCellAlignToStyle: t.tableCellAlignToStyle !== !1,
    },
    o = em(i, e, void 0);
  return o && typeof o != "string"
    ? o
    : i.create(e, i.Fragment, { children: o || void 0 }, void 0);
}
function em(e, t, n) {
  if (t.type === "element") return Hx(e, t, n);
  if (t.type === "mdxFlowExpression" || t.type === "mdxTextExpression")
    return jx(e, t);
  if (t.type === "mdxJsxFlowElement" || t.type === "mdxJsxTextElement")
    return Gx(e, t, n);
  if (t.type === "mdxjsEsm") return Wx(e, t);
  if (t.type === "root") return Kx(e, t, n);
  if (t.type === "text") return Vx(e, t);
}
function Hx(e, t, n) {
  const r = e.schema;
  let i = r;
  (t.tagName.toLowerCase() === "svg" &&
    r.space === "html" &&
    ((i = oc), (e.schema = i)),
    e.ancestors.push(t));
  const o = nm(e, t.tagName, !1),
    l = Qx(e, t);
  let a = cc(e, t);
  return (
    Bx.has(t.tagName) &&
      (a = a.filter(function (s) {
        return typeof s == "string" ? !Qw(s) : !0;
      })),
    tm(e, l, o, t),
    uc(l, a),
    e.ancestors.pop(),
    (e.schema = r),
    e.create(t, o, l, n)
  );
}
function jx(e, t) {
  if (t.data && t.data.estree && e.evaluater) {
    const r = t.data.estree.body[0];
    return (r.type, e.evaluater.evaluateExpression(r.expression));
  }
  Vi(e, t.position);
}
function Wx(e, t) {
  if (t.data && t.data.estree && e.evaluater)
    return e.evaluater.evaluateProgram(t.data.estree);
  Vi(e, t.position);
}
function Gx(e, t, n) {
  const r = e.schema;
  let i = r;
  (t.name === "svg" && r.space === "html" && ((i = oc), (e.schema = i)),
    e.ancestors.push(t));
  const o = t.name === null ? e.Fragment : nm(e, t.name, !0),
    l = Zx(e, t),
    a = cc(e, t);
  return (
    tm(e, l, o, t),
    uc(l, a),
    e.ancestors.pop(),
    (e.schema = r),
    e.create(t, o, l, n)
  );
}
function Kx(e, t, n) {
  const r = {};
  return (uc(r, cc(e, t)), e.create(t, e.Fragment, r, n));
}
function Vx(e, t) {
  return t.value;
}
function tm(e, t, n, r) {
  typeof n != "string" && n !== e.Fragment && e.passNode && (t.node = r);
}
function uc(e, t) {
  if (t.length > 0) {
    const n = t.length > 1 ? t : t[0];
    n && (e.children = n);
  }
}
function qx(e, t, n) {
  return r;
  function r(i, o, l, a) {
    const u = Array.isArray(l.children) ? n : t;
    return a ? u(o, l, a) : u(o, l);
  }
}
function Yx(e, t) {
  return n;
  function n(r, i, o, l) {
    const a = Array.isArray(o.children),
      s = ac(r);
    return t(
      i,
      o,
      l,
      a,
      {
        columnNumber: s ? s.column - 1 : void 0,
        fileName: e,
        lineNumber: s ? s.line : void 0,
      },
      void 0,
    );
  }
}
function Qx(e, t) {
  const n = {};
  let r, i;
  for (i in t.properties)
    if (i !== "children" && sc.call(t.properties, i)) {
      const o = Xx(e, i, t.properties[i]);
      if (o) {
        const [l, a] = o;
        e.tableCellAlignToStyle &&
        l === "align" &&
        typeof a == "string" &&
        Ux.has(t.tagName)
          ? (r = a)
          : (n[l] = a);
      }
    }
  if (r) {
    const o = n.style || (n.style = {});
    o[e.stylePropertyNameCase === "css" ? "text-align" : "textAlign"] = r;
  }
  return n;
}
function Zx(e, t) {
  const n = {};
  for (const r of t.attributes)
    if (r.type === "mdxJsxExpressionAttribute")
      if (r.data && r.data.estree && e.evaluater) {
        const o = r.data.estree.body[0];
        o.type;
        const l = o.expression;
        l.type;
        const a = l.properties[0];
        (a.type, Object.assign(n, e.evaluater.evaluateExpression(a.argument)));
      } else Vi(e, t.position);
    else {
      const i = r.name;
      let o;
      if (r.value && typeof r.value == "object")
        if (r.value.data && r.value.data.estree && e.evaluater) {
          const a = r.value.data.estree.body[0];
          (a.type, (o = e.evaluater.evaluateExpression(a.expression)));
        } else Vi(e, t.position);
      else o = r.value === null ? !0 : r.value;
      n[i] = o;
    }
  return n;
}
function cc(e, t) {
  const n = [];
  let r = -1;
  const i = e.passKeys ? new Map() : zx;
  for (; ++r < t.children.length;) {
    const o = t.children[r];
    let l;
    if (e.passKeys) {
      const s =
        o.type === "element"
          ? o.tagName
          : o.type === "mdxJsxFlowElement" || o.type === "mdxJsxTextElement"
            ? o.name
            : void 0;
      if (s) {
        const u = i.get(s) || 0;
        ((l = s + "-" + u), i.set(s, u + 1));
      }
    }
    const a = em(e, o, l);
    a !== void 0 && n.push(a);
  }
  return n;
}
function Xx(e, t, n) {
  const r = rx(e.schema, t);
  if (!(n == null || (typeof n == "number" && Number.isNaN(n)))) {
    if (
      (Array.isArray(n) && (n = r.commaSeparated ? Gw(n) : ax(n)),
      r.property === "style")
    ) {
      let i = typeof n == "object" ? n : Jx(e, String(n));
      return (e.stylePropertyNameCase === "css" && (i = e_(i)), ["style", i]);
    }
    return [
      e.elementAttributeNameCase === "react" && r.space
        ? ex[r.property] || r.property
        : r.attribute,
      n,
    ];
  }
}
function Jx(e, t) {
  try {
    return Dx(t, { reactCompat: !0 });
  } catch (n) {
    if (e.ignoreInvalidStyle) return {};
    const r = n,
      i = new Ue("Cannot parse `style` attribute", {
        ancestors: e.ancestors,
        cause: r,
        ruleId: "style",
        source: "hast-util-to-jsx-runtime",
      });
    throw (
      (i.file = e.filePath || void 0),
      (i.url = Jg + "#cannot-parse-style-attribute"),
      i
    );
  }
}
function nm(e, t, n) {
  let r;
  if (!n) r = { type: "Literal", value: t };
  else if (t.includes(".")) {
    const i = t.split(".");
    let o = -1,
      l;
    for (; ++o < i.length;) {
      const a = Yd(i[o])
        ? { type: "Identifier", name: i[o] }
        : { type: "Literal", value: i[o] };
      l = l
        ? {
            type: "MemberExpression",
            object: l,
            property: a,
            computed: !!(o && a.type === "Literal"),
            optional: !1,
          }
        : a;
    }
    r = l;
  } else
    r =
      Yd(t) && !/^[a-z]/.test(t)
        ? { type: "Identifier", name: t }
        : { type: "Literal", value: t };
  if (r.type === "Literal") {
    const i = r.value;
    return sc.call(e.components, i) ? e.components[i] : i;
  }
  if (e.evaluater) return e.evaluater.evaluateExpression(r);
  Vi(e);
}
function Vi(e, t) {
  const n = new Ue("Cannot handle MDX estrees without `createEvaluater`", {
    ancestors: e.ancestors,
    place: t,
    ruleId: "mdx-estree",
    source: "hast-util-to-jsx-runtime",
  });
  throw (
    (n.file = e.filePath || void 0),
    (n.url = Jg + "#cannot-handle-mdx-estrees-without-createevaluater"),
    n
  );
}
function e_(e) {
  const t = {};
  let n;
  for (n in e) sc.call(e, n) && (t[t_(n)] = e[n]);
  return t;
}
function t_(e) {
  let t = e.replace(Fx, n_);
  return (t.slice(0, 3) === "ms-" && (t = "-" + t), t);
}
function n_(e) {
  return "-" + e.toLowerCase();
}
const Ra = {
    action: ["form"],
    cite: ["blockquote", "del", "ins", "q"],
    data: ["object"],
    formAction: ["button", "input"],
    href: ["a", "area", "base", "link"],
    icon: ["menuitem"],
    itemId: null,
    manifest: ["html"],
    ping: ["a", "area"],
    poster: ["video"],
    src: [
      "audio",
      "embed",
      "iframe",
      "img",
      "input",
      "script",
      "source",
      "track",
      "video",
    ],
  },
  r_ = {};
function dc(e, t) {
  const n = r_,
    r = typeof n.includeImageAlt == "boolean" ? n.includeImageAlt : !0,
    i = typeof n.includeHtml == "boolean" ? n.includeHtml : !0;
  return rm(e, r, i);
}
function rm(e, t, n) {
  if (i_(e)) {
    if ("value" in e) return e.type === "html" && !n ? "" : e.value;
    if (t && "alt" in e && e.alt) return e.alt;
    if ("children" in e) return af(e.children, t, n);
  }
  return Array.isArray(e) ? af(e, t, n) : "";
}
function af(e, t, n) {
  const r = [];
  let i = -1;
  for (; ++i < e.length;) r[i] = rm(e[i], t, n);
  return r.join("");
}
function i_(e) {
  return !!(e && typeof e == "object");
}
const sf = document.createElement("i");
function fc(e) {
  const t = "&" + e + ";";
  sf.innerHTML = t;
  const n = sf.textContent;
  return (n.charCodeAt(n.length - 1) === 59 && e !== "semi") || n === t
    ? !1
    : n;
}
function st(e, t, n, r) {
  const i = e.length;
  let o = 0,
    l;
  if (
    (t < 0 ? (t = -t > i ? 0 : i + t) : (t = t > i ? i : t),
    (n = n > 0 ? n : 0),
    r.length < 1e4)
  )
    ((l = Array.from(r)), l.unshift(t, n), e.splice(...l));
  else
    for (n && e.splice(t, n); o < r.length;)
      ((l = r.slice(o, o + 1e4)),
        l.unshift(t, 0),
        e.splice(...l),
        (o += 1e4),
        (t += 1e4));
}
function ht(e, t) {
  return e.length > 0 ? (st(e, e.length, 0, t), e) : t;
}
const uf = {}.hasOwnProperty;
function im(e) {
  const t = {};
  let n = -1;
  for (; ++n < e.length;) o_(t, e[n]);
  return t;
}
function o_(e, t) {
  let n;
  for (n in t) {
    const i = (uf.call(e, n) ? e[n] : void 0) || (e[n] = {}),
      o = t[n];
    let l;
    if (o)
      for (l in o) {
        uf.call(i, l) || (i[l] = []);
        const a = o[l];
        l_(i[l], Array.isArray(a) ? a : a ? [a] : []);
      }
  }
}
function l_(e, t) {
  let n = -1;
  const r = [];
  for (; ++n < t.length;) (t[n].add === "after" ? e : r).push(t[n]);
  st(e, 0, 0, r);
}
function om(e, t) {
  const n = Number.parseInt(e, t);
  return n < 9 ||
    n === 11 ||
    (n > 13 && n < 32) ||
    (n > 126 && n < 160) ||
    (n > 55295 && n < 57344) ||
    (n > 64975 && n < 65008) ||
    (n & 65535) === 65535 ||
    (n & 65535) === 65534 ||
    n > 1114111
    ? "�"
    : String.fromCodePoint(n);
}
function Ct(e) {
  return e
    .replace(/[\t\n\r ]+/g, " ")
    .replace(/^ | $/g, "")
    .toLowerCase()
    .toUpperCase();
}
const Ge = On(/[A-Za-z]/),
  Fe = On(/[\dA-Za-z]/),
  a_ = On(/[#-'*+\--9=?A-Z^-~]/);
function _l(e) {
  return e !== null && (e < 32 || e === 127);
}
const Qs = On(/\d/),
  s_ = On(/[\dA-Fa-f]/),
  u_ = On(/[!-/:-@[-`{-~]/);
function q(e) {
  return e !== null && e < -2;
}
function de(e) {
  return e !== null && (e < 0 || e === 32);
}
function ee(e) {
  return e === -2 || e === -1 || e === 32;
}
const Yl = On(new RegExp("\\p{P}|\\p{S}", "u")),
  Zn = On(/\s/);
function On(e) {
  return t;
  function t(n) {
    return n !== null && n > -1 && e.test(String.fromCharCode(n));
  }
}
function Vr(e) {
  const t = [];
  let n = -1,
    r = 0,
    i = 0;
  for (; ++n < e.length;) {
    const o = e.charCodeAt(n);
    let l = "";
    if (o === 37 && Fe(e.charCodeAt(n + 1)) && Fe(e.charCodeAt(n + 2))) i = 2;
    else if (o < 128)
      /[!#$&-;=?-Z_a-z~]/.test(String.fromCharCode(o)) ||
        (l = String.fromCharCode(o));
    else if (o > 55295 && o < 57344) {
      const a = e.charCodeAt(n + 1);
      o < 56320 && a > 56319 && a < 57344
        ? ((l = String.fromCharCode(o, a)), (i = 1))
        : (l = "�");
    } else l = String.fromCharCode(o);
    (l &&
      (t.push(e.slice(r, n), encodeURIComponent(l)), (r = n + i + 1), (l = "")),
      i && ((n += i), (i = 0)));
  }
  return t.join("") + e.slice(r);
}
function re(e, t, n, r) {
  const i = r ? r - 1 : Number.POSITIVE_INFINITY;
  let o = 0;
  return l;
  function l(s) {
    return ee(s) ? (e.enter(n), a(s)) : t(s);
  }
  function a(s) {
    return ee(s) && o++ < i ? (e.consume(s), a) : (e.exit(n), t(s));
  }
}
const c_ = { tokenize: d_ };
function d_(e) {
  const t = e.attempt(this.parser.constructs.contentInitial, r, i);
  let n;
  return t;
  function r(a) {
    if (a === null) {
      e.consume(a);
      return;
    }
    return (
      e.enter("lineEnding"),
      e.consume(a),
      e.exit("lineEnding"),
      re(e, t, "linePrefix")
    );
  }
  function i(a) {
    return (e.enter("paragraph"), o(a));
  }
  function o(a) {
    const s = e.enter("chunkText", { contentType: "text", previous: n });
    return (n && (n.next = s), (n = s), l(a));
  }
  function l(a) {
    if (a === null) {
      (e.exit("chunkText"), e.exit("paragraph"), e.consume(a));
      return;
    }
    return q(a) ? (e.consume(a), e.exit("chunkText"), o) : (e.consume(a), l);
  }
}
const f_ = { tokenize: p_ },
  cf = { tokenize: h_ };
function p_(e) {
  const t = this,
    n = [];
  let r = 0,
    i,
    o,
    l;
  return a;
  function a(b) {
    if (r < n.length) {
      const _ = n[r];
      return ((t.containerState = _[1]), e.attempt(_[0].continuation, s, u)(b));
    }
    return u(b);
  }
  function s(b) {
    if ((r++, t.containerState._closeFlow)) {
      ((t.containerState._closeFlow = void 0), i && m());
      const _ = t.events.length;
      let N = _,
        x;
      for (; N--;)
        if (t.events[N][0] === "exit" && t.events[N][1].type === "chunkFlow") {
          x = t.events[N][1].end;
          break;
        }
      h(r);
      let O = _;
      for (; O < t.events.length;) ((t.events[O][1].end = { ...x }), O++);
      return (
        st(t.events, N + 1, 0, t.events.slice(_)),
        (t.events.length = O),
        u(b)
      );
    }
    return a(b);
  }
  function u(b) {
    if (r === n.length) {
      if (!i) return f(b);
      if (i.currentConstruct && i.currentConstruct.concrete) return g(b);
      t.interrupt = !!(i.currentConstruct && !i._gfmTableDynamicInterruptHack);
    }
    return ((t.containerState = {}), e.check(cf, d, c)(b));
  }
  function d(b) {
    return (i && m(), h(r), f(b));
  }
  function c(b) {
    return (
      (t.parser.lazy[t.now().line] = r !== n.length),
      (l = t.now().offset),
      g(b)
    );
  }
  function f(b) {
    return ((t.containerState = {}), e.attempt(cf, p, g)(b));
  }
  function p(b) {
    return (r++, n.push([t.currentConstruct, t.containerState]), f(b));
  }
  function g(b) {
    if (b === null) {
      (i && m(), h(0), e.consume(b));
      return;
    }
    return (
      (i = i || t.parser.flow(t.now())),
      e.enter("chunkFlow", { _tokenizer: i, contentType: "flow", previous: o }),
      y(b)
    );
  }
  function y(b) {
    if (b === null) {
      (E(e.exit("chunkFlow"), !0), h(0), e.consume(b));
      return;
    }
    return q(b)
      ? (e.consume(b),
        E(e.exit("chunkFlow")),
        (r = 0),
        (t.interrupt = void 0),
        a)
      : (e.consume(b), y);
  }
  function E(b, _) {
    const N = t.sliceStream(b);
    if (
      (_ && N.push(null),
      (b.previous = o),
      o && (o.next = b),
      (o = b),
      i.defineSkip(b.start),
      i.write(N),
      t.parser.lazy[b.start.line])
    ) {
      let x = i.events.length;
      for (; x--;)
        if (
          i.events[x][1].start.offset < l &&
          (!i.events[x][1].end || i.events[x][1].end.offset > l)
        )
          return;
      const O = t.events.length;
      let I = O,
        U,
        S;
      for (; I--;)
        if (t.events[I][0] === "exit" && t.events[I][1].type === "chunkFlow") {
          if (U) {
            S = t.events[I][1].end;
            break;
          }
          U = !0;
        }
      for (h(r), x = O; x < t.events.length;)
        ((t.events[x][1].end = { ...S }), x++);
      (st(t.events, I + 1, 0, t.events.slice(O)), (t.events.length = x));
    }
  }
  function h(b) {
    let _ = n.length;
    for (; _-- > b;) {
      const N = n[_];
      ((t.containerState = N[1]), N[0].exit.call(t, e));
    }
    n.length = b;
  }
  function m() {
    (i.write([null]),
      (o = void 0),
      (i = void 0),
      (t.containerState._closeFlow = void 0));
  }
}
function h_(e, t, n) {
  return re(
    e,
    e.attempt(this.parser.constructs.document, t, n),
    "linePrefix",
    this.parser.constructs.disable.null.includes("codeIndented") ? void 0 : 4,
  );
}
function Br(e) {
  if (e === null || de(e) || Zn(e)) return 1;
  if (Yl(e)) return 2;
}
function Ql(e, t, n) {
  const r = [];
  let i = -1;
  for (; ++i < e.length;) {
    const o = e[i].resolveAll;
    o && !r.includes(o) && ((t = o(t, n)), r.push(o));
  }
  return t;
}
const Zs = { name: "attention", resolveAll: g_, tokenize: m_ };
function g_(e, t) {
  let n = -1,
    r,
    i,
    o,
    l,
    a,
    s,
    u,
    d;
  for (; ++n < e.length;)
    if (
      e[n][0] === "enter" &&
      e[n][1].type === "attentionSequence" &&
      e[n][1]._close
    ) {
      for (r = n; r--;)
        if (
          e[r][0] === "exit" &&
          e[r][1].type === "attentionSequence" &&
          e[r][1]._open &&
          t.sliceSerialize(e[r][1]).charCodeAt(0) ===
            t.sliceSerialize(e[n][1]).charCodeAt(0)
        ) {
          if (
            (e[r][1]._close || e[n][1]._open) &&
            (e[n][1].end.offset - e[n][1].start.offset) % 3 &&
            !(
              (e[r][1].end.offset -
                e[r][1].start.offset +
                e[n][1].end.offset -
                e[n][1].start.offset) %
              3
            )
          )
            continue;
          s =
            e[r][1].end.offset - e[r][1].start.offset > 1 &&
            e[n][1].end.offset - e[n][1].start.offset > 1
              ? 2
              : 1;
          const c = { ...e[r][1].end },
            f = { ...e[n][1].start };
          (df(c, -s),
            df(f, s),
            (l = {
              type: s > 1 ? "strongSequence" : "emphasisSequence",
              start: c,
              end: { ...e[r][1].end },
            }),
            (a = {
              type: s > 1 ? "strongSequence" : "emphasisSequence",
              start: { ...e[n][1].start },
              end: f,
            }),
            (o = {
              type: s > 1 ? "strongText" : "emphasisText",
              start: { ...e[r][1].end },
              end: { ...e[n][1].start },
            }),
            (i = {
              type: s > 1 ? "strong" : "emphasis",
              start: { ...l.start },
              end: { ...a.end },
            }),
            (e[r][1].end = { ...l.start }),
            (e[n][1].start = { ...a.end }),
            (u = []),
            e[r][1].end.offset - e[r][1].start.offset &&
              (u = ht(u, [
                ["enter", e[r][1], t],
                ["exit", e[r][1], t],
              ])),
            (u = ht(u, [
              ["enter", i, t],
              ["enter", l, t],
              ["exit", l, t],
              ["enter", o, t],
            ])),
            (u = ht(
              u,
              Ql(t.parser.constructs.insideSpan.null, e.slice(r + 1, n), t),
            )),
            (u = ht(u, [
              ["exit", o, t],
              ["enter", a, t],
              ["exit", a, t],
              ["exit", i, t],
            ])),
            e[n][1].end.offset - e[n][1].start.offset
              ? ((d = 2),
                (u = ht(u, [
                  ["enter", e[n][1], t],
                  ["exit", e[n][1], t],
                ])))
              : (d = 0),
            st(e, r - 1, n - r + 3, u),
            (n = r + u.length - d - 2));
          break;
        }
    }
  for (n = -1; ++n < e.length;)
    e[n][1].type === "attentionSequence" && (e[n][1].type = "data");
  return e;
}
function m_(e, t) {
  const n = this.parser.constructs.attentionMarkers.null,
    r = this.previous,
    i = Br(r);
  let o;
  return l;
  function l(s) {
    return ((o = s), e.enter("attentionSequence"), a(s));
  }
  function a(s) {
    if (s === o) return (e.consume(s), a);
    const u = e.exit("attentionSequence"),
      d = Br(s),
      c = !d || (d === 2 && i) || n.includes(s),
      f = !i || (i === 2 && d) || n.includes(r);
    return (
      (u._open = !!(o === 42 ? c : c && (i || !f))),
      (u._close = !!(o === 42 ? f : f && (d || !c))),
      t(s)
    );
  }
}
function df(e, t) {
  ((e.column += t), (e.offset += t), (e._bufferIndex += t));
}
const y_ = { name: "autolink", tokenize: b_ };
function b_(e, t, n) {
  let r = 0;
  return i;
  function i(p) {
    return (
      e.enter("autolink"),
      e.enter("autolinkMarker"),
      e.consume(p),
      e.exit("autolinkMarker"),
      e.enter("autolinkProtocol"),
      o
    );
  }
  function o(p) {
    return Ge(p) ? (e.consume(p), l) : p === 64 ? n(p) : u(p);
  }
  function l(p) {
    return p === 43 || p === 45 || p === 46 || Fe(p) ? ((r = 1), a(p)) : u(p);
  }
  function a(p) {
    return p === 58
      ? (e.consume(p), (r = 0), s)
      : (p === 43 || p === 45 || p === 46 || Fe(p)) && r++ < 32
        ? (e.consume(p), a)
        : ((r = 0), u(p));
  }
  function s(p) {
    return p === 62
      ? (e.exit("autolinkProtocol"),
        e.enter("autolinkMarker"),
        e.consume(p),
        e.exit("autolinkMarker"),
        e.exit("autolink"),
        t)
      : p === null || p === 32 || p === 60 || _l(p)
        ? n(p)
        : (e.consume(p), s);
  }
  function u(p) {
    return p === 64 ? (e.consume(p), d) : a_(p) ? (e.consume(p), u) : n(p);
  }
  function d(p) {
    return Fe(p) ? c(p) : n(p);
  }
  function c(p) {
    return p === 46
      ? (e.consume(p), (r = 0), d)
      : p === 62
        ? ((e.exit("autolinkProtocol").type = "autolinkEmail"),
          e.enter("autolinkMarker"),
          e.consume(p),
          e.exit("autolinkMarker"),
          e.exit("autolink"),
          t)
        : f(p);
  }
  function f(p) {
    if ((p === 45 || Fe(p)) && r++ < 63) {
      const g = p === 45 ? f : c;
      return (e.consume(p), g);
    }
    return n(p);
  }
}
const oo = { partial: !0, tokenize: v_ };
function v_(e, t, n) {
  return r;
  function r(o) {
    return ee(o) ? re(e, i, "linePrefix")(o) : i(o);
  }
  function i(o) {
    return o === null || q(o) ? t(o) : n(o);
  }
}
const lm = {
  continuation: { tokenize: w_ },
  exit: x_,
  name: "blockQuote",
  tokenize: E_,
};
function E_(e, t, n) {
  const r = this;
  return i;
  function i(l) {
    if (l === 62) {
      const a = r.containerState;
      return (
        a.open || (e.enter("blockQuote", { _container: !0 }), (a.open = !0)),
        e.enter("blockQuotePrefix"),
        e.enter("blockQuoteMarker"),
        e.consume(l),
        e.exit("blockQuoteMarker"),
        o
      );
    }
    return n(l);
  }
  function o(l) {
    return ee(l)
      ? (e.enter("blockQuotePrefixWhitespace"),
        e.consume(l),
        e.exit("blockQuotePrefixWhitespace"),
        e.exit("blockQuotePrefix"),
        t)
      : (e.exit("blockQuotePrefix"), t(l));
  }
}
function w_(e, t, n) {
  const r = this;
  return i;
  function i(l) {
    return ee(l)
      ? re(
          e,
          o,
          "linePrefix",
          r.parser.constructs.disable.null.includes("codeIndented")
            ? void 0
            : 4,
        )(l)
      : o(l);
  }
  function o(l) {
    return e.attempt(lm, t, n)(l);
  }
}
function x_(e) {
  e.exit("blockQuote");
}
const am = { name: "characterEscape", tokenize: __ };
function __(e, t, n) {
  return r;
  function r(o) {
    return (
      e.enter("characterEscape"),
      e.enter("escapeMarker"),
      e.consume(o),
      e.exit("escapeMarker"),
      i
    );
  }
  function i(o) {
    return u_(o)
      ? (e.enter("characterEscapeValue"),
        e.consume(o),
        e.exit("characterEscapeValue"),
        e.exit("characterEscape"),
        t)
      : n(o);
  }
}
const sm = { name: "characterReference", tokenize: k_ };
function k_(e, t, n) {
  const r = this;
  let i = 0,
    o,
    l;
  return a;
  function a(c) {
    return (
      e.enter("characterReference"),
      e.enter("characterReferenceMarker"),
      e.consume(c),
      e.exit("characterReferenceMarker"),
      s
    );
  }
  function s(c) {
    return c === 35
      ? (e.enter("characterReferenceMarkerNumeric"),
        e.consume(c),
        e.exit("characterReferenceMarkerNumeric"),
        u)
      : (e.enter("characterReferenceValue"), (o = 31), (l = Fe), d(c));
  }
  function u(c) {
    return c === 88 || c === 120
      ? (e.enter("characterReferenceMarkerHexadecimal"),
        e.consume(c),
        e.exit("characterReferenceMarkerHexadecimal"),
        e.enter("characterReferenceValue"),
        (o = 6),
        (l = s_),
        d)
      : (e.enter("characterReferenceValue"), (o = 7), (l = Qs), d(c));
  }
  function d(c) {
    if (c === 59 && i) {
      const f = e.exit("characterReferenceValue");
      return l === Fe && !fc(r.sliceSerialize(f))
        ? n(c)
        : (e.enter("characterReferenceMarker"),
          e.consume(c),
          e.exit("characterReferenceMarker"),
          e.exit("characterReference"),
          t);
    }
    return l(c) && i++ < o ? (e.consume(c), d) : n(c);
  }
}
const ff = { partial: !0, tokenize: N_ },
  pf = { concrete: !0, name: "codeFenced", tokenize: S_ };
function S_(e, t, n) {
  const r = this,
    i = { partial: !0, tokenize: N };
  let o = 0,
    l = 0,
    a;
  return s;
  function s(x) {
    return u(x);
  }
  function u(x) {
    const O = r.events[r.events.length - 1];
    return (
      (o =
        O && O[1].type === "linePrefix"
          ? O[2].sliceSerialize(O[1], !0).length
          : 0),
      (a = x),
      e.enter("codeFenced"),
      e.enter("codeFencedFence"),
      e.enter("codeFencedFenceSequence"),
      d(x)
    );
  }
  function d(x) {
    return x === a
      ? (l++, e.consume(x), d)
      : l < 3
        ? n(x)
        : (e.exit("codeFencedFenceSequence"),
          ee(x) ? re(e, c, "whitespace")(x) : c(x));
  }
  function c(x) {
    return x === null || q(x)
      ? (e.exit("codeFencedFence"), r.interrupt ? t(x) : e.check(ff, y, _)(x))
      : (e.enter("codeFencedFenceInfo"),
        e.enter("chunkString", { contentType: "string" }),
        f(x));
  }
  function f(x) {
    return x === null || q(x)
      ? (e.exit("chunkString"), e.exit("codeFencedFenceInfo"), c(x))
      : ee(x)
        ? (e.exit("chunkString"),
          e.exit("codeFencedFenceInfo"),
          re(e, p, "whitespace")(x))
        : x === 96 && x === a
          ? n(x)
          : (e.consume(x), f);
  }
  function p(x) {
    return x === null || q(x)
      ? c(x)
      : (e.enter("codeFencedFenceMeta"),
        e.enter("chunkString", { contentType: "string" }),
        g(x));
  }
  function g(x) {
    return x === null || q(x)
      ? (e.exit("chunkString"), e.exit("codeFencedFenceMeta"), c(x))
      : x === 96 && x === a
        ? n(x)
        : (e.consume(x), g);
  }
  function y(x) {
    return e.attempt(i, _, E)(x);
  }
  function E(x) {
    return (e.enter("lineEnding"), e.consume(x), e.exit("lineEnding"), h);
  }
  function h(x) {
    return o > 0 && ee(x) ? re(e, m, "linePrefix", o + 1)(x) : m(x);
  }
  function m(x) {
    return x === null || q(x)
      ? e.check(ff, y, _)(x)
      : (e.enter("codeFlowValue"), b(x));
  }
  function b(x) {
    return x === null || q(x)
      ? (e.exit("codeFlowValue"), m(x))
      : (e.consume(x), b);
  }
  function _(x) {
    return (e.exit("codeFenced"), t(x));
  }
  function N(x, O, I) {
    let U = 0;
    return S;
    function S(G) {
      return (x.enter("lineEnding"), x.consume(G), x.exit("lineEnding"), F);
    }
    function F(G) {
      return (
        x.enter("codeFencedFence"),
        ee(G)
          ? re(
              x,
              L,
              "linePrefix",
              r.parser.constructs.disable.null.includes("codeIndented")
                ? void 0
                : 4,
            )(G)
          : L(G)
      );
    }
    function L(G) {
      return G === a ? (x.enter("codeFencedFenceSequence"), Q(G)) : I(G);
    }
    function Q(G) {
      return G === a
        ? (U++, x.consume(G), Q)
        : U >= l
          ? (x.exit("codeFencedFenceSequence"),
            ee(G) ? re(x, V, "whitespace")(G) : V(G))
          : I(G);
    }
    function V(G) {
      return G === null || q(G) ? (x.exit("codeFencedFence"), O(G)) : I(G);
    }
  }
}
function N_(e, t, n) {
  const r = this;
  return i;
  function i(l) {
    return l === null
      ? n(l)
      : (e.enter("lineEnding"), e.consume(l), e.exit("lineEnding"), o);
  }
  function o(l) {
    return r.parser.lazy[r.now().line] ? n(l) : t(l);
  }
}
const Oa = { name: "codeIndented", tokenize: T_ },
  C_ = { partial: !0, tokenize: A_ };
function T_(e, t, n) {
  const r = this;
  return i;
  function i(u) {
    return (e.enter("codeIndented"), re(e, o, "linePrefix", 5)(u));
  }
  function o(u) {
    const d = r.events[r.events.length - 1];
    return d &&
      d[1].type === "linePrefix" &&
      d[2].sliceSerialize(d[1], !0).length >= 4
      ? l(u)
      : n(u);
  }
  function l(u) {
    return u === null
      ? s(u)
      : q(u)
        ? e.attempt(C_, l, s)(u)
        : (e.enter("codeFlowValue"), a(u));
  }
  function a(u) {
    return u === null || q(u)
      ? (e.exit("codeFlowValue"), l(u))
      : (e.consume(u), a);
  }
  function s(u) {
    return (e.exit("codeIndented"), t(u));
  }
}
function A_(e, t, n) {
  const r = this;
  return i;
  function i(l) {
    return r.parser.lazy[r.now().line]
      ? n(l)
      : q(l)
        ? (e.enter("lineEnding"), e.consume(l), e.exit("lineEnding"), i)
        : re(e, o, "linePrefix", 5)(l);
  }
  function o(l) {
    const a = r.events[r.events.length - 1];
    return a &&
      a[1].type === "linePrefix" &&
      a[2].sliceSerialize(a[1], !0).length >= 4
      ? t(l)
      : q(l)
        ? i(l)
        : n(l);
  }
}
const R_ = { name: "codeText", previous: I_, resolve: O_, tokenize: M_ };
function O_(e) {
  let t = e.length - 4,
    n = 3,
    r,
    i;
  if (
    (e[n][1].type === "lineEnding" || e[n][1].type === "space") &&
    (e[t][1].type === "lineEnding" || e[t][1].type === "space")
  ) {
    for (r = n; ++r < t;)
      if (e[r][1].type === "codeTextData") {
        ((e[n][1].type = "codeTextPadding"),
          (e[t][1].type = "codeTextPadding"),
          (n += 2),
          (t -= 2));
        break;
      }
  }
  for (r = n - 1, t++; ++r <= t;)
    i === void 0
      ? r !== t && e[r][1].type !== "lineEnding" && (i = r)
      : (r === t || e[r][1].type === "lineEnding") &&
        ((e[i][1].type = "codeTextData"),
        r !== i + 2 &&
          ((e[i][1].end = e[r - 1][1].end),
          e.splice(i + 2, r - i - 2),
          (t -= r - i - 2),
          (r = i + 2)),
        (i = void 0));
  return e;
}
function I_(e) {
  return (
    e !== 96 ||
    this.events[this.events.length - 1][1].type === "characterEscape"
  );
}
function M_(e, t, n) {
  let r = 0,
    i,
    o;
  return l;
  function l(c) {
    return (e.enter("codeText"), e.enter("codeTextSequence"), a(c));
  }
  function a(c) {
    return c === 96
      ? (e.consume(c), r++, a)
      : (e.exit("codeTextSequence"), s(c));
  }
  function s(c) {
    return c === null
      ? n(c)
      : c === 32
        ? (e.enter("space"), e.consume(c), e.exit("space"), s)
        : c === 96
          ? ((o = e.enter("codeTextSequence")), (i = 0), d(c))
          : q(c)
            ? (e.enter("lineEnding"), e.consume(c), e.exit("lineEnding"), s)
            : (e.enter("codeTextData"), u(c));
  }
  function u(c) {
    return c === null || c === 32 || c === 96 || q(c)
      ? (e.exit("codeTextData"), s(c))
      : (e.consume(c), u);
  }
  function d(c) {
    return c === 96
      ? (e.consume(c), i++, d)
      : i === r
        ? (e.exit("codeTextSequence"), e.exit("codeText"), t(c))
        : ((o.type = "codeTextData"), u(c));
  }
}
class L_ {
  constructor(t) {
    ((this.left = t ? [...t] : []), (this.right = []));
  }
  get(t) {
    if (t < 0 || t >= this.left.length + this.right.length)
      throw new RangeError(
        "Cannot access index `" +
          t +
          "` in a splice buffer of size `" +
          (this.left.length + this.right.length) +
          "`",
      );
    return t < this.left.length
      ? this.left[t]
      : this.right[this.right.length - t + this.left.length - 1];
  }
  get length() {
    return this.left.length + this.right.length;
  }
  shift() {
    return (this.setCursor(0), this.right.pop());
  }
  slice(t, n) {
    const r = n ?? Number.POSITIVE_INFINITY;
    return r < this.left.length
      ? this.left.slice(t, r)
      : t > this.left.length
        ? this.right
            .slice(
              this.right.length - r + this.left.length,
              this.right.length - t + this.left.length,
            )
            .reverse()
        : this.left
            .slice(t)
            .concat(
              this.right
                .slice(this.right.length - r + this.left.length)
                .reverse(),
            );
  }
  splice(t, n, r) {
    const i = n || 0;
    this.setCursor(Math.trunc(t));
    const o = this.right.splice(
      this.right.length - i,
      Number.POSITIVE_INFINITY,
    );
    return (r && ui(this.left, r), o.reverse());
  }
  pop() {
    return (this.setCursor(Number.POSITIVE_INFINITY), this.left.pop());
  }
  push(t) {
    (this.setCursor(Number.POSITIVE_INFINITY), this.left.push(t));
  }
  pushMany(t) {
    (this.setCursor(Number.POSITIVE_INFINITY), ui(this.left, t));
  }
  unshift(t) {
    (this.setCursor(0), this.right.push(t));
  }
  unshiftMany(t) {
    (this.setCursor(0), ui(this.right, t.reverse()));
  }
  setCursor(t) {
    if (!(
      t === this.left.length ||
      (t > this.left.length && this.right.length === 0) ||
      (t < 0 && this.left.length === 0)
    ))
      if (t < this.left.length) {
        const n = this.left.splice(t, Number.POSITIVE_INFINITY);
        ui(this.right, n.reverse());
      } else {
        const n = this.right.splice(
          this.left.length + this.right.length - t,
          Number.POSITIVE_INFINITY,
        );
        ui(this.left, n.reverse());
      }
  }
}
function ui(e, t) {
  let n = 0;
  if (t.length < 1e4) e.push(...t);
  else for (; n < t.length;) (e.push(...t.slice(n, n + 1e4)), (n += 1e4));
}
function um(e) {
  const t = {};
  let n = -1,
    r,
    i,
    o,
    l,
    a,
    s,
    u;
  const d = new L_(e);
  for (; ++n < d.length;) {
    for (; n in t;) n = t[n];
    if (
      ((r = d.get(n)),
      n &&
        r[1].type === "chunkFlow" &&
        d.get(n - 1)[1].type === "listItemPrefix" &&
        ((s = r[1]._tokenizer.events),
        (o = 0),
        o < s.length && s[o][1].type === "lineEndingBlank" && (o += 2),
        o < s.length && s[o][1].type === "content"))
    )
      for (; ++o < s.length && s[o][1].type !== "content";)
        s[o][1].type === "chunkText" &&
          ((s[o][1]._isInFirstContentOfListItem = !0), o++);
    if (r[0] === "enter")
      r[1].contentType && (Object.assign(t, D_(d, n)), (n = t[n]), (u = !0));
    else if (r[1]._container) {
      for (o = n, i = void 0; o--;)
        if (
          ((l = d.get(o)),
          l[1].type === "lineEnding" || l[1].type === "lineEndingBlank")
        )
          l[0] === "enter" &&
            (i && (d.get(i)[1].type = "lineEndingBlank"),
            (l[1].type = "lineEnding"),
            (i = o));
        else if (!(
          l[1].type === "linePrefix" || l[1].type === "listItemIndent"
        ))
          break;
      i &&
        ((r[1].end = { ...d.get(i)[1].start }),
        (a = d.slice(i, n)),
        a.unshift(r),
        d.splice(i, n - i + 1, a));
    }
  }
  return (st(e, 0, Number.POSITIVE_INFINITY, d.slice(0)), !u);
}
function D_(e, t) {
  const n = e.get(t)[1],
    r = e.get(t)[2];
  let i = t - 1;
  const o = [];
  let l = n._tokenizer;
  l ||
    ((l = r.parser[n.contentType](n.start)),
    n._contentTypeTextTrailing && (l._contentTypeTextTrailing = !0));
  const a = l.events,
    s = [],
    u = {};
  let d,
    c,
    f = -1,
    p = n,
    g = 0,
    y = 0;
  const E = [y];
  for (; p;) {
    for (; e.get(++i)[1] !== p;);
    (o.push(i),
      p._tokenizer ||
        ((d = r.sliceStream(p)),
        p.next || d.push(null),
        c && l.defineSkip(p.start),
        p._isInFirstContentOfListItem &&
          (l._gfmTasklistFirstContentOfListItem = !0),
        l.write(d),
        p._isInFirstContentOfListItem &&
          (l._gfmTasklistFirstContentOfListItem = void 0)),
      (c = p),
      (p = p.next));
  }
  for (p = n; ++f < a.length;)
    a[f][0] === "exit" &&
      a[f - 1][0] === "enter" &&
      a[f][1].type === a[f - 1][1].type &&
      a[f][1].start.line !== a[f][1].end.line &&
      ((y = f + 1),
      E.push(y),
      (p._tokenizer = void 0),
      (p.previous = void 0),
      (p = p.next));
  for (
    l.events = [],
      p ? ((p._tokenizer = void 0), (p.previous = void 0)) : E.pop(),
      f = E.length;
    f--;
  ) {
    const h = a.slice(E[f], E[f + 1]),
      m = o.pop();
    (s.push([m, m + h.length - 1]), e.splice(m, 2, h));
  }
  for (s.reverse(), f = -1; ++f < s.length;)
    ((u[g + s[f][0]] = g + s[f][1]), (g += s[f][1] - s[f][0] - 1));
  return u;
}
const P_ = { resolve: F_, tokenize: B_ },
  z_ = { partial: !0, tokenize: U_ };
function F_(e) {
  return (um(e), e);
}
function B_(e, t) {
  let n;
  return r;
  function r(a) {
    return (
      e.enter("content"),
      (n = e.enter("chunkContent", { contentType: "content" })),
      i(a)
    );
  }
  function i(a) {
    return a === null ? o(a) : q(a) ? e.check(z_, l, o)(a) : (e.consume(a), i);
  }
  function o(a) {
    return (e.exit("chunkContent"), e.exit("content"), t(a));
  }
  function l(a) {
    return (
      e.consume(a),
      e.exit("chunkContent"),
      (n.next = e.enter("chunkContent", {
        contentType: "content",
        previous: n,
      })),
      (n = n.next),
      i
    );
  }
}
function U_(e, t, n) {
  const r = this;
  return i;
  function i(l) {
    return (
      e.exit("chunkContent"),
      e.enter("lineEnding"),
      e.consume(l),
      e.exit("lineEnding"),
      re(e, o, "linePrefix")
    );
  }
  function o(l) {
    if (l === null || q(l)) return n(l);
    const a = r.events[r.events.length - 1];
    return !r.parser.constructs.disable.null.includes("codeIndented") &&
      a &&
      a[1].type === "linePrefix" &&
      a[2].sliceSerialize(a[1], !0).length >= 4
      ? t(l)
      : e.interrupt(r.parser.constructs.flow, n, t)(l);
  }
}
function cm(e, t, n, r, i, o, l, a, s) {
  const u = s || Number.POSITIVE_INFINITY;
  let d = 0;
  return c;
  function c(h) {
    return h === 60
      ? (e.enter(r), e.enter(i), e.enter(o), e.consume(h), e.exit(o), f)
      : h === null || h === 32 || h === 41 || _l(h)
        ? n(h)
        : (e.enter(r),
          e.enter(l),
          e.enter(a),
          e.enter("chunkString", { contentType: "string" }),
          y(h));
  }
  function f(h) {
    return h === 62
      ? (e.enter(o), e.consume(h), e.exit(o), e.exit(i), e.exit(r), t)
      : (e.enter(a), e.enter("chunkString", { contentType: "string" }), p(h));
  }
  function p(h) {
    return h === 62
      ? (e.exit("chunkString"), e.exit(a), f(h))
      : h === null || h === 60 || q(h)
        ? n(h)
        : (e.consume(h), h === 92 ? g : p);
  }
  function g(h) {
    return h === 60 || h === 62 || h === 92 ? (e.consume(h), p) : p(h);
  }
  function y(h) {
    return !d && (h === null || h === 41 || de(h))
      ? (e.exit("chunkString"), e.exit(a), e.exit(l), e.exit(r), t(h))
      : d < u && h === 40
        ? (e.consume(h), d++, y)
        : h === 41
          ? (e.consume(h), d--, y)
          : h === null || h === 32 || h === 40 || _l(h)
            ? n(h)
            : (e.consume(h), h === 92 ? E : y);
  }
  function E(h) {
    return h === 40 || h === 41 || h === 92 ? (e.consume(h), y) : y(h);
  }
}
function dm(e, t, n, r, i, o) {
  const l = this;
  let a = 0,
    s;
  return u;
  function u(p) {
    return (e.enter(r), e.enter(i), e.consume(p), e.exit(i), e.enter(o), d);
  }
  function d(p) {
    return a > 999 ||
      p === null ||
      p === 91 ||
      (p === 93 && !s) ||
      (p === 94 && !a && "_hiddenFootnoteSupport" in l.parser.constructs)
      ? n(p)
      : p === 93
        ? (e.exit(o), e.enter(i), e.consume(p), e.exit(i), e.exit(r), t)
        : q(p)
          ? (e.enter("lineEnding"), e.consume(p), e.exit("lineEnding"), d)
          : (e.enter("chunkString", { contentType: "string" }), c(p));
  }
  function c(p) {
    return p === null || p === 91 || p === 93 || q(p) || a++ > 999
      ? (e.exit("chunkString"), d(p))
      : (e.consume(p), s || (s = !ee(p)), p === 92 ? f : c);
  }
  function f(p) {
    return p === 91 || p === 92 || p === 93 ? (e.consume(p), a++, c) : c(p);
  }
}
function fm(e, t, n, r, i, o) {
  let l;
  return a;
  function a(f) {
    return f === 34 || f === 39 || f === 40
      ? (e.enter(r),
        e.enter(i),
        e.consume(f),
        e.exit(i),
        (l = f === 40 ? 41 : f),
        s)
      : n(f);
  }
  function s(f) {
    return f === l
      ? (e.enter(i), e.consume(f), e.exit(i), e.exit(r), t)
      : (e.enter(o), u(f));
  }
  function u(f) {
    return f === l
      ? (e.exit(o), s(l))
      : f === null
        ? n(f)
        : q(f)
          ? (e.enter("lineEnding"),
            e.consume(f),
            e.exit("lineEnding"),
            re(e, u, "linePrefix"))
          : (e.enter("chunkString", { contentType: "string" }), d(f));
  }
  function d(f) {
    return f === l || f === null || q(f)
      ? (e.exit("chunkString"), u(f))
      : (e.consume(f), f === 92 ? c : d);
  }
  function c(f) {
    return f === l || f === 92 ? (e.consume(f), d) : d(f);
  }
}
function Ni(e, t) {
  let n;
  return r;
  function r(i) {
    return q(i)
      ? (e.enter("lineEnding"), e.consume(i), e.exit("lineEnding"), (n = !0), r)
      : ee(i)
        ? re(e, r, n ? "linePrefix" : "lineSuffix")(i)
        : t(i);
  }
}
const $_ = { name: "definition", tokenize: j_ },
  H_ = { partial: !0, tokenize: W_ };
function j_(e, t, n) {
  const r = this;
  let i;
  return o;
  function o(p) {
    return (e.enter("definition"), l(p));
  }
  function l(p) {
    return dm.call(
      r,
      e,
      a,
      n,
      "definitionLabel",
      "definitionLabelMarker",
      "definitionLabelString",
    )(p);
  }
  function a(p) {
    return (
      (i = Ct(r.sliceSerialize(r.events[r.events.length - 1][1]).slice(1, -1))),
      p === 58
        ? (e.enter("definitionMarker"),
          e.consume(p),
          e.exit("definitionMarker"),
          s)
        : n(p)
    );
  }
  function s(p) {
    return de(p) ? Ni(e, u)(p) : u(p);
  }
  function u(p) {
    return cm(
      e,
      d,
      n,
      "definitionDestination",
      "definitionDestinationLiteral",
      "definitionDestinationLiteralMarker",
      "definitionDestinationRaw",
      "definitionDestinationString",
    )(p);
  }
  function d(p) {
    return e.attempt(H_, c, c)(p);
  }
  function c(p) {
    return ee(p) ? re(e, f, "whitespace")(p) : f(p);
  }
  function f(p) {
    return p === null || q(p)
      ? (e.exit("definition"), r.parser.defined.push(i), t(p))
      : n(p);
  }
}
function W_(e, t, n) {
  return r;
  function r(a) {
    return de(a) ? Ni(e, i)(a) : n(a);
  }
  function i(a) {
    return fm(
      e,
      o,
      n,
      "definitionTitle",
      "definitionTitleMarker",
      "definitionTitleString",
    )(a);
  }
  function o(a) {
    return ee(a) ? re(e, l, "whitespace")(a) : l(a);
  }
  function l(a) {
    return a === null || q(a) ? t(a) : n(a);
  }
}
const G_ = { name: "hardBreakEscape", tokenize: K_ };
function K_(e, t, n) {
  return r;
  function r(o) {
    return (e.enter("hardBreakEscape"), e.consume(o), i);
  }
  function i(o) {
    return q(o) ? (e.exit("hardBreakEscape"), t(o)) : n(o);
  }
}
const V_ = { name: "headingAtx", resolve: q_, tokenize: Y_ };
function q_(e, t) {
  let n = e.length - 2,
    r = 3,
    i,
    o;
  return (
    e[r][1].type === "whitespace" && (r += 2),
    n - 2 > r && e[n][1].type === "whitespace" && (n -= 2),
    e[n][1].type === "atxHeadingSequence" &&
      (r === n - 1 || (n - 4 > r && e[n - 2][1].type === "whitespace")) &&
      (n -= r + 1 === n ? 2 : 4),
    n > r &&
      ((i = { type: "atxHeadingText", start: e[r][1].start, end: e[n][1].end }),
      (o = {
        type: "chunkText",
        start: e[r][1].start,
        end: e[n][1].end,
        contentType: "text",
      }),
      st(e, r, n - r + 1, [
        ["enter", i, t],
        ["enter", o, t],
        ["exit", o, t],
        ["exit", i, t],
      ])),
    e
  );
}
function Y_(e, t, n) {
  let r = 0;
  return i;
  function i(d) {
    return (e.enter("atxHeading"), o(d));
  }
  function o(d) {
    return (e.enter("atxHeadingSequence"), l(d));
  }
  function l(d) {
    return d === 35 && r++ < 6
      ? (e.consume(d), l)
      : d === null || de(d)
        ? (e.exit("atxHeadingSequence"), a(d))
        : n(d);
  }
  function a(d) {
    return d === 35
      ? (e.enter("atxHeadingSequence"), s(d))
      : d === null || q(d)
        ? (e.exit("atxHeading"), t(d))
        : ee(d)
          ? re(e, a, "whitespace")(d)
          : (e.enter("atxHeadingText"), u(d));
  }
  function s(d) {
    return d === 35 ? (e.consume(d), s) : (e.exit("atxHeadingSequence"), a(d));
  }
  function u(d) {
    return d === null || d === 35 || de(d)
      ? (e.exit("atxHeadingText"), a(d))
      : (e.consume(d), u);
  }
}
const Q_ = [
    "address",
    "article",
    "aside",
    "base",
    "basefont",
    "blockquote",
    "body",
    "caption",
    "center",
    "col",
    "colgroup",
    "dd",
    "details",
    "dialog",
    "dir",
    "div",
    "dl",
    "dt",
    "fieldset",
    "figcaption",
    "figure",
    "footer",
    "form",
    "frame",
    "frameset",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "head",
    "header",
    "hr",
    "html",
    "iframe",
    "legend",
    "li",
    "link",
    "main",
    "menu",
    "menuitem",
    "nav",
    "noframes",
    "ol",
    "optgroup",
    "option",
    "p",
    "param",
    "search",
    "section",
    "summary",
    "table",
    "tbody",
    "td",
    "tfoot",
    "th",
    "thead",
    "title",
    "tr",
    "track",
    "ul",
  ],
  hf = ["pre", "script", "style", "textarea"],
  Z_ = { concrete: !0, name: "htmlFlow", resolveTo: e0, tokenize: t0 },
  X_ = { partial: !0, tokenize: r0 },
  J_ = { partial: !0, tokenize: n0 };
function e0(e) {
  let t = e.length;
  for (; t-- && !(e[t][0] === "enter" && e[t][1].type === "htmlFlow"););
  return (
    t > 1 &&
      e[t - 2][1].type === "linePrefix" &&
      ((e[t][1].start = e[t - 2][1].start),
      (e[t + 1][1].start = e[t - 2][1].start),
      e.splice(t - 2, 2)),
    e
  );
}
function t0(e, t, n) {
  const r = this;
  let i, o, l, a, s;
  return u;
  function u(w) {
    return d(w);
  }
  function d(w) {
    return (e.enter("htmlFlow"), e.enter("htmlFlowData"), e.consume(w), c);
  }
  function c(w) {
    return w === 33
      ? (e.consume(w), f)
      : w === 47
        ? (e.consume(w), (o = !0), y)
        : w === 63
          ? (e.consume(w), (i = 3), r.interrupt ? t : v)
          : Ge(w)
            ? (e.consume(w), (l = String.fromCharCode(w)), E)
            : n(w);
  }
  function f(w) {
    return w === 45
      ? (e.consume(w), (i = 2), p)
      : w === 91
        ? (e.consume(w), (i = 5), (a = 0), g)
        : Ge(w)
          ? (e.consume(w), (i = 4), r.interrupt ? t : v)
          : n(w);
  }
  function p(w) {
    return w === 45 ? (e.consume(w), r.interrupt ? t : v) : n(w);
  }
  function g(w) {
    const ne = "CDATA[";
    return w === ne.charCodeAt(a++)
      ? (e.consume(w), a === ne.length ? (r.interrupt ? t : L) : g)
      : n(w);
  }
  function y(w) {
    return Ge(w) ? (e.consume(w), (l = String.fromCharCode(w)), E) : n(w);
  }
  function E(w) {
    if (w === null || w === 47 || w === 62 || de(w)) {
      const ne = w === 47,
        pe = l.toLowerCase();
      return !ne && !o && hf.includes(pe)
        ? ((i = 1), r.interrupt ? t(w) : L(w))
        : Q_.includes(l.toLowerCase())
          ? ((i = 6), ne ? (e.consume(w), h) : r.interrupt ? t(w) : L(w))
          : ((i = 7),
            r.interrupt && !r.parser.lazy[r.now().line]
              ? n(w)
              : o
                ? m(w)
                : b(w));
    }
    return w === 45 || Fe(w)
      ? (e.consume(w), (l += String.fromCharCode(w)), E)
      : n(w);
  }
  function h(w) {
    return w === 62 ? (e.consume(w), r.interrupt ? t : L) : n(w);
  }
  function m(w) {
    return ee(w) ? (e.consume(w), m) : S(w);
  }
  function b(w) {
    return w === 47
      ? (e.consume(w), S)
      : w === 58 || w === 95 || Ge(w)
        ? (e.consume(w), _)
        : ee(w)
          ? (e.consume(w), b)
          : S(w);
  }
  function _(w) {
    return w === 45 || w === 46 || w === 58 || w === 95 || Fe(w)
      ? (e.consume(w), _)
      : N(w);
  }
  function N(w) {
    return w === 61 ? (e.consume(w), x) : ee(w) ? (e.consume(w), N) : b(w);
  }
  function x(w) {
    return w === null || w === 60 || w === 61 || w === 62 || w === 96
      ? n(w)
      : w === 34 || w === 39
        ? (e.consume(w), (s = w), O)
        : ee(w)
          ? (e.consume(w), x)
          : I(w);
  }
  function O(w) {
    return w === s
      ? (e.consume(w), (s = null), U)
      : w === null || q(w)
        ? n(w)
        : (e.consume(w), O);
  }
  function I(w) {
    return w === null ||
      w === 34 ||
      w === 39 ||
      w === 47 ||
      w === 60 ||
      w === 61 ||
      w === 62 ||
      w === 96 ||
      de(w)
      ? N(w)
      : (e.consume(w), I);
  }
  function U(w) {
    return w === 47 || w === 62 || ee(w) ? b(w) : n(w);
  }
  function S(w) {
    return w === 62 ? (e.consume(w), F) : n(w);
  }
  function F(w) {
    return w === null || q(w) ? L(w) : ee(w) ? (e.consume(w), F) : n(w);
  }
  function L(w) {
    return w === 45 && i === 2
      ? (e.consume(w), R)
      : w === 60 && i === 1
        ? (e.consume(w), B)
        : w === 62 && i === 4
          ? (e.consume(w), H)
          : w === 63 && i === 3
            ? (e.consume(w), v)
            : w === 93 && i === 5
              ? (e.consume(w), M)
              : q(w) && (i === 6 || i === 7)
                ? (e.exit("htmlFlowData"), e.check(X_, K, Q)(w))
                : w === null || q(w)
                  ? (e.exit("htmlFlowData"), Q(w))
                  : (e.consume(w), L);
  }
  function Q(w) {
    return e.check(J_, V, K)(w);
  }
  function V(w) {
    return (e.enter("lineEnding"), e.consume(w), e.exit("lineEnding"), G);
  }
  function G(w) {
    return w === null || q(w) ? Q(w) : (e.enter("htmlFlowData"), L(w));
  }
  function R(w) {
    return w === 45 ? (e.consume(w), v) : L(w);
  }
  function B(w) {
    return w === 47 ? (e.consume(w), (l = ""), C) : L(w);
  }
  function C(w) {
    if (w === 62) {
      const ne = l.toLowerCase();
      return hf.includes(ne) ? (e.consume(w), H) : L(w);
    }
    return Ge(w) && l.length < 8
      ? (e.consume(w), (l += String.fromCharCode(w)), C)
      : L(w);
  }
  function M(w) {
    return w === 93 ? (e.consume(w), v) : L(w);
  }
  function v(w) {
    return w === 62
      ? (e.consume(w), H)
      : w === 45 && i === 2
        ? (e.consume(w), v)
        : L(w);
  }
  function H(w) {
    return w === null || q(w)
      ? (e.exit("htmlFlowData"), K(w))
      : (e.consume(w), H);
  }
  function K(w) {
    return (e.exit("htmlFlow"), t(w));
  }
}
function n0(e, t, n) {
  const r = this;
  return i;
  function i(l) {
    return q(l)
      ? (e.enter("lineEnding"), e.consume(l), e.exit("lineEnding"), o)
      : n(l);
  }
  function o(l) {
    return r.parser.lazy[r.now().line] ? n(l) : t(l);
  }
}
function r0(e, t, n) {
  return r;
  function r(i) {
    return (
      e.enter("lineEnding"),
      e.consume(i),
      e.exit("lineEnding"),
      e.attempt(oo, t, n)
    );
  }
}
const i0 = { name: "htmlText", tokenize: o0 };
function o0(e, t, n) {
  const r = this;
  let i, o, l;
  return a;
  function a(v) {
    return (e.enter("htmlText"), e.enter("htmlTextData"), e.consume(v), s);
  }
  function s(v) {
    return v === 33
      ? (e.consume(v), u)
      : v === 47
        ? (e.consume(v), N)
        : v === 63
          ? (e.consume(v), b)
          : Ge(v)
            ? (e.consume(v), I)
            : n(v);
  }
  function u(v) {
    return v === 45
      ? (e.consume(v), d)
      : v === 91
        ? (e.consume(v), (o = 0), g)
        : Ge(v)
          ? (e.consume(v), m)
          : n(v);
  }
  function d(v) {
    return v === 45 ? (e.consume(v), p) : n(v);
  }
  function c(v) {
    return v === null
      ? n(v)
      : v === 45
        ? (e.consume(v), f)
        : q(v)
          ? ((l = c), B(v))
          : (e.consume(v), c);
  }
  function f(v) {
    return v === 45 ? (e.consume(v), p) : c(v);
  }
  function p(v) {
    return v === 62 ? R(v) : v === 45 ? f(v) : c(v);
  }
  function g(v) {
    const H = "CDATA[";
    return v === H.charCodeAt(o++)
      ? (e.consume(v), o === H.length ? y : g)
      : n(v);
  }
  function y(v) {
    return v === null
      ? n(v)
      : v === 93
        ? (e.consume(v), E)
        : q(v)
          ? ((l = y), B(v))
          : (e.consume(v), y);
  }
  function E(v) {
    return v === 93 ? (e.consume(v), h) : y(v);
  }
  function h(v) {
    return v === 62 ? R(v) : v === 93 ? (e.consume(v), h) : y(v);
  }
  function m(v) {
    return v === null || v === 62
      ? R(v)
      : q(v)
        ? ((l = m), B(v))
        : (e.consume(v), m);
  }
  function b(v) {
    return v === null
      ? n(v)
      : v === 63
        ? (e.consume(v), _)
        : q(v)
          ? ((l = b), B(v))
          : (e.consume(v), b);
  }
  function _(v) {
    return v === 62 ? R(v) : b(v);
  }
  function N(v) {
    return Ge(v) ? (e.consume(v), x) : n(v);
  }
  function x(v) {
    return v === 45 || Fe(v) ? (e.consume(v), x) : O(v);
  }
  function O(v) {
    return q(v) ? ((l = O), B(v)) : ee(v) ? (e.consume(v), O) : R(v);
  }
  function I(v) {
    return v === 45 || Fe(v)
      ? (e.consume(v), I)
      : v === 47 || v === 62 || de(v)
        ? U(v)
        : n(v);
  }
  function U(v) {
    return v === 47
      ? (e.consume(v), R)
      : v === 58 || v === 95 || Ge(v)
        ? (e.consume(v), S)
        : q(v)
          ? ((l = U), B(v))
          : ee(v)
            ? (e.consume(v), U)
            : R(v);
  }
  function S(v) {
    return v === 45 || v === 46 || v === 58 || v === 95 || Fe(v)
      ? (e.consume(v), S)
      : F(v);
  }
  function F(v) {
    return v === 61
      ? (e.consume(v), L)
      : q(v)
        ? ((l = F), B(v))
        : ee(v)
          ? (e.consume(v), F)
          : U(v);
  }
  function L(v) {
    return v === null || v === 60 || v === 61 || v === 62 || v === 96
      ? n(v)
      : v === 34 || v === 39
        ? (e.consume(v), (i = v), Q)
        : q(v)
          ? ((l = L), B(v))
          : ee(v)
            ? (e.consume(v), L)
            : (e.consume(v), V);
  }
  function Q(v) {
    return v === i
      ? (e.consume(v), (i = void 0), G)
      : v === null
        ? n(v)
        : q(v)
          ? ((l = Q), B(v))
          : (e.consume(v), Q);
  }
  function V(v) {
    return v === null ||
      v === 34 ||
      v === 39 ||
      v === 60 ||
      v === 61 ||
      v === 96
      ? n(v)
      : v === 47 || v === 62 || de(v)
        ? U(v)
        : (e.consume(v), V);
  }
  function G(v) {
    return v === 47 || v === 62 || de(v) ? U(v) : n(v);
  }
  function R(v) {
    return v === 62
      ? (e.consume(v), e.exit("htmlTextData"), e.exit("htmlText"), t)
      : n(v);
  }
  function B(v) {
    return (
      e.exit("htmlTextData"),
      e.enter("lineEnding"),
      e.consume(v),
      e.exit("lineEnding"),
      C
    );
  }
  function C(v) {
    return ee(v)
      ? re(
          e,
          M,
          "linePrefix",
          r.parser.constructs.disable.null.includes("codeIndented")
            ? void 0
            : 4,
        )(v)
      : M(v);
  }
  function M(v) {
    return (e.enter("htmlTextData"), l(v));
  }
}
const pc = { name: "labelEnd", resolveAll: u0, resolveTo: c0, tokenize: d0 },
  l0 = { tokenize: f0 },
  a0 = { tokenize: p0 },
  s0 = { tokenize: h0 };
function u0(e) {
  let t = -1;
  const n = [];
  for (; ++t < e.length;) {
    const r = e[t][1];
    if (
      (n.push(e[t]),
      r.type === "labelImage" ||
        r.type === "labelLink" ||
        r.type === "labelEnd")
    ) {
      const i = r.type === "labelImage" ? 4 : 2;
      ((r.type = "data"), (t += i));
    }
  }
  return (e.length !== n.length && st(e, 0, e.length, n), e);
}
function c0(e, t) {
  let n = e.length,
    r = 0,
    i,
    o,
    l,
    a;
  for (; n--;)
    if (((i = e[n][1]), o)) {
      if (i.type === "link" || (i.type === "labelLink" && i._inactive)) break;
      e[n][0] === "enter" && i.type === "labelLink" && (i._inactive = !0);
    } else if (l) {
      if (
        e[n][0] === "enter" &&
        (i.type === "labelImage" || i.type === "labelLink") &&
        !i._balanced &&
        ((o = n), i.type !== "labelLink")
      ) {
        r = 2;
        break;
      }
    } else i.type === "labelEnd" && (l = n);
  const s = {
      type: e[o][1].type === "labelLink" ? "link" : "image",
      start: { ...e[o][1].start },
      end: { ...e[e.length - 1][1].end },
    },
    u = { type: "label", start: { ...e[o][1].start }, end: { ...e[l][1].end } },
    d = {
      type: "labelText",
      start: { ...e[o + r + 2][1].end },
      end: { ...e[l - 2][1].start },
    };
  return (
    (a = [
      ["enter", s, t],
      ["enter", u, t],
    ]),
    (a = ht(a, e.slice(o + 1, o + r + 3))),
    (a = ht(a, [["enter", d, t]])),
    (a = ht(
      a,
      Ql(t.parser.constructs.insideSpan.null, e.slice(o + r + 4, l - 3), t),
    )),
    (a = ht(a, [["exit", d, t], e[l - 2], e[l - 1], ["exit", u, t]])),
    (a = ht(a, e.slice(l + 1))),
    (a = ht(a, [["exit", s, t]])),
    st(e, o, e.length, a),
    e
  );
}
function d0(e, t, n) {
  const r = this;
  let i = r.events.length,
    o,
    l;
  for (; i--;)
    if (
      (r.events[i][1].type === "labelImage" ||
        r.events[i][1].type === "labelLink") &&
      !r.events[i][1]._balanced
    ) {
      o = r.events[i][1];
      break;
    }
  return a;
  function a(f) {
    return o
      ? o._inactive
        ? c(f)
        : ((l = r.parser.defined.includes(
            Ct(r.sliceSerialize({ start: o.end, end: r.now() })),
          )),
          e.enter("labelEnd"),
          e.enter("labelMarker"),
          e.consume(f),
          e.exit("labelMarker"),
          e.exit("labelEnd"),
          s)
      : n(f);
  }
  function s(f) {
    return f === 40
      ? e.attempt(l0, d, l ? d : c)(f)
      : f === 91
        ? e.attempt(a0, d, l ? u : c)(f)
        : l
          ? d(f)
          : c(f);
  }
  function u(f) {
    return e.attempt(s0, d, c)(f);
  }
  function d(f) {
    return t(f);
  }
  function c(f) {
    return ((o._balanced = !0), n(f));
  }
}
function f0(e, t, n) {
  return r;
  function r(c) {
    return (
      e.enter("resource"),
      e.enter("resourceMarker"),
      e.consume(c),
      e.exit("resourceMarker"),
      i
    );
  }
  function i(c) {
    return de(c) ? Ni(e, o)(c) : o(c);
  }
  function o(c) {
    return c === 41
      ? d(c)
      : cm(
          e,
          l,
          a,
          "resourceDestination",
          "resourceDestinationLiteral",
          "resourceDestinationLiteralMarker",
          "resourceDestinationRaw",
          "resourceDestinationString",
          32,
        )(c);
  }
  function l(c) {
    return de(c) ? Ni(e, s)(c) : d(c);
  }
  function a(c) {
    return n(c);
  }
  function s(c) {
    return c === 34 || c === 39 || c === 40
      ? fm(
          e,
          u,
          n,
          "resourceTitle",
          "resourceTitleMarker",
          "resourceTitleString",
        )(c)
      : d(c);
  }
  function u(c) {
    return de(c) ? Ni(e, d)(c) : d(c);
  }
  function d(c) {
    return c === 41
      ? (e.enter("resourceMarker"),
        e.consume(c),
        e.exit("resourceMarker"),
        e.exit("resource"),
        t)
      : n(c);
  }
}
function p0(e, t, n) {
  const r = this;
  return i;
  function i(a) {
    return dm.call(
      r,
      e,
      o,
      l,
      "reference",
      "referenceMarker",
      "referenceString",
    )(a);
  }
  function o(a) {
    return r.parser.defined.includes(
      Ct(r.sliceSerialize(r.events[r.events.length - 1][1]).slice(1, -1)),
    )
      ? t(a)
      : n(a);
  }
  function l(a) {
    return n(a);
  }
}
function h0(e, t, n) {
  return r;
  function r(o) {
    return (
      e.enter("reference"),
      e.enter("referenceMarker"),
      e.consume(o),
      e.exit("referenceMarker"),
      i
    );
  }
  function i(o) {
    return o === 93
      ? (e.enter("referenceMarker"),
        e.consume(o),
        e.exit("referenceMarker"),
        e.exit("reference"),
        t)
      : n(o);
  }
}
const g0 = { name: "labelStartImage", resolveAll: pc.resolveAll, tokenize: m0 };
function m0(e, t, n) {
  const r = this;
  return i;
  function i(a) {
    return (
      e.enter("labelImage"),
      e.enter("labelImageMarker"),
      e.consume(a),
      e.exit("labelImageMarker"),
      o
    );
  }
  function o(a) {
    return a === 91
      ? (e.enter("labelMarker"),
        e.consume(a),
        e.exit("labelMarker"),
        e.exit("labelImage"),
        l)
      : n(a);
  }
  function l(a) {
    return a === 94 && "_hiddenFootnoteSupport" in r.parser.constructs
      ? n(a)
      : t(a);
  }
}
const y0 = { name: "labelStartLink", resolveAll: pc.resolveAll, tokenize: b0 };
function b0(e, t, n) {
  const r = this;
  return i;
  function i(l) {
    return (
      e.enter("labelLink"),
      e.enter("labelMarker"),
      e.consume(l),
      e.exit("labelMarker"),
      e.exit("labelLink"),
      o
    );
  }
  function o(l) {
    return l === 94 && "_hiddenFootnoteSupport" in r.parser.constructs
      ? n(l)
      : t(l);
  }
}
const Ia = { name: "lineEnding", tokenize: v0 };
function v0(e, t) {
  return n;
  function n(r) {
    return (
      e.enter("lineEnding"),
      e.consume(r),
      e.exit("lineEnding"),
      re(e, t, "linePrefix")
    );
  }
}
const Yo = { name: "thematicBreak", tokenize: E0 };
function E0(e, t, n) {
  let r = 0,
    i;
  return o;
  function o(u) {
    return (e.enter("thematicBreak"), l(u));
  }
  function l(u) {
    return ((i = u), a(u));
  }
  function a(u) {
    return u === i
      ? (e.enter("thematicBreakSequence"), s(u))
      : r >= 3 && (u === null || q(u))
        ? (e.exit("thematicBreak"), t(u))
        : n(u);
  }
  function s(u) {
    return u === i
      ? (e.consume(u), r++, s)
      : (e.exit("thematicBreakSequence"),
        ee(u) ? re(e, a, "whitespace")(u) : a(u));
  }
}
const Qe = {
    continuation: { tokenize: k0 },
    exit: N0,
    name: "list",
    tokenize: _0,
  },
  w0 = { partial: !0, tokenize: C0 },
  x0 = { partial: !0, tokenize: S0 };
function _0(e, t, n) {
  const r = this,
    i = r.events[r.events.length - 1];
  let o =
      i && i[1].type === "linePrefix"
        ? i[2].sliceSerialize(i[1], !0).length
        : 0,
    l = 0;
  return a;
  function a(p) {
    const g =
      r.containerState.type ||
      (p === 42 || p === 43 || p === 45 ? "listUnordered" : "listOrdered");
    if (
      g === "listUnordered"
        ? !r.containerState.marker || p === r.containerState.marker
        : Qs(p)
    ) {
      if (
        (r.containerState.type ||
          ((r.containerState.type = g), e.enter(g, { _container: !0 })),
        g === "listUnordered")
      )
        return (
          e.enter("listItemPrefix"),
          p === 42 || p === 45 ? e.check(Yo, n, u)(p) : u(p)
        );
      if (!r.interrupt || p === 49)
        return (e.enter("listItemPrefix"), e.enter("listItemValue"), s(p));
    }
    return n(p);
  }
  function s(p) {
    return Qs(p) && ++l < 10
      ? (e.consume(p), s)
      : (!r.interrupt || l < 2) &&
          (r.containerState.marker
            ? p === r.containerState.marker
            : p === 41 || p === 46)
        ? (e.exit("listItemValue"), u(p))
        : n(p);
  }
  function u(p) {
    return (
      e.enter("listItemMarker"),
      e.consume(p),
      e.exit("listItemMarker"),
      (r.containerState.marker = r.containerState.marker || p),
      e.check(oo, r.interrupt ? n : d, e.attempt(w0, f, c))
    );
  }
  function d(p) {
    return ((r.containerState.initialBlankLine = !0), o++, f(p));
  }
  function c(p) {
    return ee(p)
      ? (e.enter("listItemPrefixWhitespace"),
        e.consume(p),
        e.exit("listItemPrefixWhitespace"),
        f)
      : n(p);
  }
  function f(p) {
    return (
      (r.containerState.size =
        o + r.sliceSerialize(e.exit("listItemPrefix"), !0).length),
      t(p)
    );
  }
}
function k0(e, t, n) {
  const r = this;
  return ((r.containerState._closeFlow = void 0), e.check(oo, i, o));
  function i(a) {
    return (
      (r.containerState.furtherBlankLines =
        r.containerState.furtherBlankLines ||
        r.containerState.initialBlankLine),
      re(e, t, "listItemIndent", r.containerState.size + 1)(a)
    );
  }
  function o(a) {
    return r.containerState.furtherBlankLines || !ee(a)
      ? ((r.containerState.furtherBlankLines = void 0),
        (r.containerState.initialBlankLine = void 0),
        l(a))
      : ((r.containerState.furtherBlankLines = void 0),
        (r.containerState.initialBlankLine = void 0),
        e.attempt(x0, t, l)(a));
  }
  function l(a) {
    return (
      (r.containerState._closeFlow = !0),
      (r.interrupt = void 0),
      re(
        e,
        e.attempt(Qe, t, n),
        "linePrefix",
        r.parser.constructs.disable.null.includes("codeIndented") ? void 0 : 4,
      )(a)
    );
  }
}
function S0(e, t, n) {
  const r = this;
  return re(e, i, "listItemIndent", r.containerState.size + 1);
  function i(o) {
    const l = r.events[r.events.length - 1];
    return l &&
      l[1].type === "listItemIndent" &&
      l[2].sliceSerialize(l[1], !0).length === r.containerState.size
      ? t(o)
      : n(o);
  }
}
function N0(e) {
  e.exit(this.containerState.type);
}
function C0(e, t, n) {
  const r = this;
  return re(
    e,
    i,
    "listItemPrefixWhitespace",
    r.parser.constructs.disable.null.includes("codeIndented") ? void 0 : 5,
  );
  function i(o) {
    const l = r.events[r.events.length - 1];
    return !ee(o) && l && l[1].type === "listItemPrefixWhitespace"
      ? t(o)
      : n(o);
  }
}
const gf = { name: "setextUnderline", resolveTo: T0, tokenize: A0 };
function T0(e, t) {
  let n = e.length,
    r,
    i,
    o;
  for (; n--;)
    if (e[n][0] === "enter") {
      if (e[n][1].type === "content") {
        r = n;
        break;
      }
      e[n][1].type === "paragraph" && (i = n);
    } else
      (e[n][1].type === "content" && e.splice(n, 1),
        !o && e[n][1].type === "definition" && (o = n));
  const l = {
    type: "setextHeading",
    start: { ...e[r][1].start },
    end: { ...e[e.length - 1][1].end },
  };
  return (
    (e[i][1].type = "setextHeadingText"),
    o
      ? (e.splice(i, 0, ["enter", l, t]),
        e.splice(o + 1, 0, ["exit", e[r][1], t]),
        (e[r][1].end = { ...e[o][1].end }))
      : (e[r][1] = l),
    e.push(["exit", l, t]),
    e
  );
}
function A0(e, t, n) {
  const r = this;
  let i;
  return o;
  function o(u) {
    let d = r.events.length,
      c;
    for (; d--;)
      if (
        r.events[d][1].type !== "lineEnding" &&
        r.events[d][1].type !== "linePrefix" &&
        r.events[d][1].type !== "content"
      ) {
        c = r.events[d][1].type === "paragraph";
        break;
      }
    return !r.parser.lazy[r.now().line] && (r.interrupt || c)
      ? (e.enter("setextHeadingLine"), (i = u), l(u))
      : n(u);
  }
  function l(u) {
    return (e.enter("setextHeadingLineSequence"), a(u));
  }
  function a(u) {
    return u === i
      ? (e.consume(u), a)
      : (e.exit("setextHeadingLineSequence"),
        ee(u) ? re(e, s, "lineSuffix")(u) : s(u));
  }
  function s(u) {
    return u === null || q(u) ? (e.exit("setextHeadingLine"), t(u)) : n(u);
  }
}
const R0 = { tokenize: O0 };
function O0(e) {
  const t = this,
    n = e.attempt(
      oo,
      r,
      e.attempt(
        this.parser.constructs.flowInitial,
        i,
        re(
          e,
          e.attempt(this.parser.constructs.flow, i, e.attempt(P_, i)),
          "linePrefix",
        ),
      ),
    );
  return n;
  function r(o) {
    if (o === null) {
      e.consume(o);
      return;
    }
    return (
      e.enter("lineEndingBlank"),
      e.consume(o),
      e.exit("lineEndingBlank"),
      (t.currentConstruct = void 0),
      n
    );
  }
  function i(o) {
    if (o === null) {
      e.consume(o);
      return;
    }
    return (
      e.enter("lineEnding"),
      e.consume(o),
      e.exit("lineEnding"),
      (t.currentConstruct = void 0),
      n
    );
  }
}
const I0 = { resolveAll: hm() },
  M0 = pm("string"),
  L0 = pm("text");
function pm(e) {
  return { resolveAll: hm(e === "text" ? D0 : void 0), tokenize: t };
  function t(n) {
    const r = this,
      i = this.parser.constructs[e],
      o = n.attempt(i, l, a);
    return l;
    function l(d) {
      return u(d) ? o(d) : a(d);
    }
    function a(d) {
      if (d === null) {
        n.consume(d);
        return;
      }
      return (n.enter("data"), n.consume(d), s);
    }
    function s(d) {
      return u(d) ? (n.exit("data"), o(d)) : (n.consume(d), s);
    }
    function u(d) {
      if (d === null) return !0;
      const c = i[d];
      let f = -1;
      if (c)
        for (; ++f < c.length;) {
          const p = c[f];
          if (!p.previous || p.previous.call(r, r.previous)) return !0;
        }
      return !1;
    }
  }
}
function hm(e) {
  return t;
  function t(n, r) {
    let i = -1,
      o;
    for (; ++i <= n.length;)
      o === void 0
        ? n[i] && n[i][1].type === "data" && ((o = i), i++)
        : (!n[i] || n[i][1].type !== "data") &&
          (i !== o + 2 &&
            ((n[o][1].end = n[i - 1][1].end),
            n.splice(o + 2, i - o - 2),
            (i = o + 2)),
          (o = void 0));
    return e ? e(n, r) : n;
  }
}
function D0(e, t) {
  let n = 0;
  for (; ++n <= e.length;)
    if (
      (n === e.length || e[n][1].type === "lineEnding") &&
      e[n - 1][1].type === "data"
    ) {
      const r = e[n - 1][1],
        i = t.sliceStream(r);
      let o = i.length,
        l = -1,
        a = 0,
        s;
      for (; o--;) {
        const u = i[o];
        if (typeof u == "string") {
          for (l = u.length; u.charCodeAt(l - 1) === 32;) (a++, l--);
          if (l) break;
          l = -1;
        } else if (u === -2) ((s = !0), a++);
        else if (u !== -1) {
          o++;
          break;
        }
      }
      if ((t._contentTypeTextTrailing && n === e.length && (a = 0), a)) {
        const u = {
          type:
            n === e.length || s || a < 2 ? "lineSuffix" : "hardBreakTrailing",
          start: {
            _bufferIndex: o ? l : r.start._bufferIndex + l,
            _index: r.start._index + o,
            line: r.end.line,
            column: r.end.column - a,
            offset: r.end.offset - a,
          },
          end: { ...r.end },
        };
        ((r.end = { ...u.start }),
          r.start.offset === r.end.offset
            ? Object.assign(r, u)
            : (e.splice(n, 0, ["enter", u, t], ["exit", u, t]), (n += 2)));
      }
      n++;
    }
  return e;
}
const P0 = {
    42: Qe,
    43: Qe,
    45: Qe,
    48: Qe,
    49: Qe,
    50: Qe,
    51: Qe,
    52: Qe,
    53: Qe,
    54: Qe,
    55: Qe,
    56: Qe,
    57: Qe,
    62: lm,
  },
  z0 = { 91: $_ },
  F0 = { [-2]: Oa, [-1]: Oa, 32: Oa },
  B0 = {
    35: V_,
    42: Yo,
    45: [gf, Yo],
    60: Z_,
    61: gf,
    95: Yo,
    96: pf,
    126: pf,
  },
  U0 = { 38: sm, 92: am },
  $0 = {
    [-5]: Ia,
    [-4]: Ia,
    [-3]: Ia,
    33: g0,
    38: sm,
    42: Zs,
    60: [y_, i0],
    91: y0,
    92: [G_, am],
    93: pc,
    95: Zs,
    96: R_,
  },
  H0 = { null: [Zs, I0] },
  j0 = { null: [42, 95] },
  W0 = { null: [] },
  G0 = Object.freeze(
    Object.defineProperty(
      {
        __proto__: null,
        attentionMarkers: j0,
        contentInitial: z0,
        disable: W0,
        document: P0,
        flow: B0,
        flowInitial: F0,
        insideSpan: H0,
        string: U0,
        text: $0,
      },
      Symbol.toStringTag,
      { value: "Module" },
    ),
  );
function K0(e, t, n) {
  let r = {
    _bufferIndex: -1,
    _index: 0,
    line: (n && n.line) || 1,
    column: (n && n.column) || 1,
    offset: (n && n.offset) || 0,
  };
  const i = {},
    o = [];
  let l = [],
    a = [];
  const s = {
      attempt: O(N),
      check: O(x),
      consume: m,
      enter: b,
      exit: _,
      interrupt: O(x, { interrupt: !0 }),
    },
    u = {
      code: null,
      containerState: {},
      defineSkip: y,
      events: [],
      now: g,
      parser: e,
      previous: null,
      sliceSerialize: f,
      sliceStream: p,
      write: c,
    };
  let d = t.tokenize.call(u, s);
  return (t.resolveAll && o.push(t), u);
  function c(F) {
    return (
      (l = ht(l, F)),
      E(),
      l[l.length - 1] !== null
        ? []
        : (I(t, 0), (u.events = Ql(o, u.events, u)), u.events)
    );
  }
  function f(F, L) {
    return q0(p(F), L);
  }
  function p(F) {
    return V0(l, F);
  }
  function g() {
    const { _bufferIndex: F, _index: L, line: Q, column: V, offset: G } = r;
    return { _bufferIndex: F, _index: L, line: Q, column: V, offset: G };
  }
  function y(F) {
    ((i[F.line] = F.column), S());
  }
  function E() {
    let F;
    for (; r._index < l.length;) {
      const L = l[r._index];
      if (typeof L == "string")
        for (
          F = r._index, r._bufferIndex < 0 && (r._bufferIndex = 0);
          r._index === F && r._bufferIndex < L.length;
        )
          h(L.charCodeAt(r._bufferIndex));
      else h(L);
    }
  }
  function h(F) {
    d = d(F);
  }
  function m(F) {
    (q(F)
      ? (r.line++, (r.column = 1), (r.offset += F === -3 ? 2 : 1), S())
      : F !== -1 && (r.column++, r.offset++),
      r._bufferIndex < 0
        ? r._index++
        : (r._bufferIndex++,
          r._bufferIndex === l[r._index].length &&
            ((r._bufferIndex = -1), r._index++)),
      (u.previous = F));
  }
  function b(F, L) {
    const Q = L || {};
    return (
      (Q.type = F),
      (Q.start = g()),
      u.events.push(["enter", Q, u]),
      a.push(Q),
      Q
    );
  }
  function _(F) {
    const L = a.pop();
    return ((L.end = g()), u.events.push(["exit", L, u]), L);
  }
  function N(F, L) {
    I(F, L.from);
  }
  function x(F, L) {
    L.restore();
  }
  function O(F, L) {
    return Q;
    function Q(V, G, R) {
      let B, C, M, v;
      return Array.isArray(V) ? K(V) : "tokenize" in V ? K([V]) : H(V);
      function H(oe) {
        return $e;
        function $e(Ye) {
          const Rt = Ye !== null && oe[Ye],
            Ot = Ye !== null && oe.null,
            nn = [
              ...(Array.isArray(Rt) ? Rt : Rt ? [Rt] : []),
              ...(Array.isArray(Ot) ? Ot : Ot ? [Ot] : []),
            ];
          return K(nn)(Ye);
        }
      }
      function K(oe) {
        return ((B = oe), (C = 0), oe.length === 0 ? R : w(oe[C]));
      }
      function w(oe) {
        return $e;
        function $e(Ye) {
          return (
            (v = U()),
            (M = oe),
            oe.partial || (u.currentConstruct = oe),
            oe.name && u.parser.constructs.disable.null.includes(oe.name)
              ? pe()
              : oe.tokenize.call(
                  L ? Object.assign(Object.create(u), L) : u,
                  s,
                  ne,
                  pe,
                )(Ye)
          );
        }
      }
      function ne(oe) {
        return (F(M, v), G);
      }
      function pe(oe) {
        return (v.restore(), ++C < B.length ? w(B[C]) : R);
      }
    }
  }
  function I(F, L) {
    (F.resolveAll && !o.includes(F) && o.push(F),
      F.resolve &&
        st(u.events, L, u.events.length - L, F.resolve(u.events.slice(L), u)),
      F.resolveTo && (u.events = F.resolveTo(u.events, u)));
  }
  function U() {
    const F = g(),
      L = u.previous,
      Q = u.currentConstruct,
      V = u.events.length,
      G = Array.from(a);
    return { from: V, restore: R };
    function R() {
      ((r = F),
        (u.previous = L),
        (u.currentConstruct = Q),
        (u.events.length = V),
        (a = G),
        S());
    }
  }
  function S() {
    r.line in i &&
      r.column < 2 &&
      ((r.column = i[r.line]), (r.offset += i[r.line] - 1));
  }
}
function V0(e, t) {
  const n = t.start._index,
    r = t.start._bufferIndex,
    i = t.end._index,
    o = t.end._bufferIndex;
  let l;
  if (n === i) l = [e[n].slice(r, o)];
  else {
    if (((l = e.slice(n, i)), r > -1)) {
      const a = l[0];
      typeof a == "string" ? (l[0] = a.slice(r)) : l.shift();
    }
    o > 0 && l.push(e[i].slice(0, o));
  }
  return l;
}
function q0(e, t) {
  let n = -1;
  const r = [];
  let i;
  for (; ++n < e.length;) {
    const o = e[n];
    let l;
    if (typeof o == "string") l = o;
    else
      switch (o) {
        case -5: {
          l = "\r";
          break;
        }
        case -4: {
          l = `
`;
          break;
        }
        case -3: {
          l = `\r
`;
          break;
        }
        case -2: {
          l = t ? " " : "	";
          break;
        }
        case -1: {
          if (!t && i) continue;
          l = " ";
          break;
        }
        default:
          l = String.fromCharCode(o);
      }
    ((i = o === -2), r.push(l));
  }
  return r.join("");
}
function Y0(e) {
  const r = {
    constructs: im([G0, ...((e || {}).extensions || [])]),
    content: i(c_),
    defined: [],
    document: i(f_),
    flow: i(R0),
    lazy: {},
    string: i(M0),
    text: i(L0),
  };
  return r;
  function i(o) {
    return l;
    function l(a) {
      return K0(r, o, a);
    }
  }
}
function Q0(e) {
  for (; !um(e););
  return e;
}
const mf = /[\0\t\n\r]/g;
function Z0() {
  let e = 1,
    t = "",
    n = !0,
    r;
  return i;
  function i(o, l, a) {
    const s = [];
    let u, d, c, f, p;
    for (
      o =
        t +
        (typeof o == "string"
          ? o.toString()
          : new TextDecoder(l || void 0).decode(o)),
        c = 0,
        t = "",
        n && (o.charCodeAt(0) === 65279 && c++, (n = void 0));
      c < o.length;
    ) {
      if (
        ((mf.lastIndex = c),
        (u = mf.exec(o)),
        (f = u && u.index !== void 0 ? u.index : o.length),
        (p = o.charCodeAt(f)),
        !u)
      ) {
        t = o.slice(c);
        break;
      }
      if (p === 10 && c === f && r) (s.push(-3), (r = void 0));
      else
        switch (
          (r && (s.push(-5), (r = void 0)),
          c < f && (s.push(o.slice(c, f)), (e += f - c)),
          p)
        ) {
          case 0: {
            (s.push(65533), e++);
            break;
          }
          case 9: {
            for (d = Math.ceil(e / 4) * 4, s.push(-2); e++ < d;) s.push(-1);
            break;
          }
          case 10: {
            (s.push(-4), (e = 1));
            break;
          }
          default:
            ((r = !0), (e = 1));
        }
      c = f + 1;
    }
    return (a && (r && s.push(-5), t && s.push(t), s.push(null)), s);
  }
}
const X0 = /\\([!-/:-@[-`{-~])|&(#(?:\d{1,7}|x[\da-f]{1,6})|[\da-z]{1,31});/gi;
function J0(e) {
  return e.replace(X0, ek);
}
function ek(e, t, n) {
  if (t) return t;
  if (n.charCodeAt(0) === 35) {
    const i = n.charCodeAt(1),
      o = i === 120 || i === 88;
    return om(n.slice(o ? 2 : 1), o ? 16 : 10);
  }
  return fc(n) || e;
}
const gm = {}.hasOwnProperty;
function tk(e, t, n) {
  return (
    t && typeof t == "object" && ((n = t), (t = void 0)),
    nk(n)(
      Q0(
        Y0(n)
          .document()
          .write(Z0()(e, t, !0)),
      ),
    )
  );
}
function nk(e) {
  const t = {
    transforms: [],
    canContainEols: ["emphasis", "fragment", "heading", "paragraph", "strong"],
    enter: {
      autolink: o(In),
      autolinkProtocol: U,
      autolinkEmail: U,
      atxHeading: o(He),
      blockQuote: o(Ot),
      characterEscape: U,
      characterReference: U,
      codeFenced: o(nn),
      codeFencedFenceInfo: l,
      codeFencedFenceMeta: l,
      codeIndented: o(nn, l),
      codeText: o(qr, l),
      codeTextData: U,
      data: U,
      codeFlowValue: U,
      definition: o(rn),
      definitionDestinationString: l,
      definitionLabelString: l,
      definitionTitleString: l,
      emphasis: o(ir),
      hardBreakEscape: o(le),
      hardBreakTrailing: o(le),
      htmlFlow: o(vt, l),
      htmlFlowData: U,
      htmlText: o(vt, l),
      htmlTextData: U,
      image: o(Y),
      label: l,
      link: o(In),
      listItem: o(se),
      listItemValue: f,
      listOrdered: o(ke, c),
      listUnordered: o(ke),
      paragraph: o(or),
      reference: w,
      referenceString: l,
      resourceDestinationString: l,
      resourceTitleString: l,
      setextHeading: o(He),
      strong: o(Ut),
      thematicBreak: o(Qr),
    },
    exit: {
      atxHeading: s(),
      atxHeadingSequence: N,
      autolink: s(),
      autolinkEmail: Rt,
      autolinkProtocol: Ye,
      blockQuote: s(),
      characterEscapeValue: S,
      characterReferenceMarkerHexadecimal: pe,
      characterReferenceMarkerNumeric: pe,
      characterReferenceValue: oe,
      characterReference: $e,
      codeFenced: s(E),
      codeFencedFence: y,
      codeFencedFenceInfo: p,
      codeFencedFenceMeta: g,
      codeFlowValue: S,
      codeIndented: s(h),
      codeText: s(G),
      codeTextData: S,
      data: S,
      definition: s(),
      definitionDestinationString: _,
      definitionLabelString: m,
      definitionTitleString: b,
      emphasis: s(),
      hardBreakEscape: s(L),
      hardBreakTrailing: s(L),
      htmlFlow: s(Q),
      htmlFlowData: S,
      htmlText: s(V),
      htmlTextData: S,
      image: s(B),
      label: M,
      labelText: C,
      lineEnding: F,
      link: s(R),
      listItem: s(),
      listOrdered: s(),
      listUnordered: s(),
      paragraph: s(),
      referenceString: ne,
      resourceDestinationString: v,
      resourceTitleString: H,
      resource: K,
      setextHeading: s(I),
      setextHeadingLineSequence: O,
      setextHeadingText: x,
      strong: s(),
      thematicBreak: s(),
    },
  };
  mm(t, (e || {}).mdastExtensions || []);
  const n = {};
  return r;
  function r(k) {
    let A = { type: "root", children: [] };
    const $ = {
        stack: [A],
        tokenStack: [],
        config: t,
        enter: a,
        exit: u,
        buffer: l,
        resume: d,
        data: n,
      },
      W = [];
    let X = -1;
    for (; ++X < k.length;)
      if (k[X][1].type === "listOrdered" || k[X][1].type === "listUnordered")
        if (k[X][0] === "enter") W.push(X);
        else {
          const xe = W.pop();
          X = i(k, xe, X);
        }
    for (X = -1; ++X < k.length;) {
      const xe = t[k[X][0]];
      gm.call(xe, k[X][1].type) &&
        xe[k[X][1].type].call(
          Object.assign({ sliceSerialize: k[X][2].sliceSerialize }, $),
          k[X][1],
        );
    }
    if ($.tokenStack.length > 0) {
      const xe = $.tokenStack[$.tokenStack.length - 1];
      (xe[1] || yf).call($, void 0, xe[0]);
    }
    for (
      A.position = {
        start: un(
          k.length > 0 ? k[0][1].start : { line: 1, column: 1, offset: 0 },
        ),
        end: un(
          k.length > 0
            ? k[k.length - 2][1].end
            : { line: 1, column: 1, offset: 0 },
        ),
      },
        X = -1;
      ++X < t.transforms.length;
    )
      A = t.transforms[X](A) || A;
    return A;
  }
  function i(k, A, $) {
    let W = A - 1,
      X = -1,
      xe = !1,
      $t,
      Et,
      Zr,
      Xr;
    for (; ++W <= $;) {
      const rt = k[W];
      switch (rt[1].type) {
        case "listUnordered":
        case "listOrdered":
        case "blockQuote": {
          (rt[0] === "enter" ? X++ : X--, (Xr = void 0));
          break;
        }
        case "lineEndingBlank": {
          rt[0] === "enter" &&
            ($t && !Xr && !X && !Zr && (Zr = W), (Xr = void 0));
          break;
        }
        case "linePrefix":
        case "listItemValue":
        case "listItemMarker":
        case "listItemPrefix":
        case "listItemPrefixWhitespace":
          break;
        default:
          Xr = void 0;
      }
      if (
        (!X && rt[0] === "enter" && rt[1].type === "listItemPrefix") ||
        (X === -1 &&
          rt[0] === "exit" &&
          (rt[1].type === "listUnordered" || rt[1].type === "listOrdered"))
      ) {
        if ($t) {
          let lr = W;
          for (Et = void 0; lr--;) {
            const Ht = k[lr];
            if (
              Ht[1].type === "lineEnding" ||
              Ht[1].type === "lineEndingBlank"
            ) {
              if (Ht[0] === "exit") continue;
              (Et && ((k[Et][1].type = "lineEndingBlank"), (xe = !0)),
                (Ht[1].type = "lineEnding"),
                (Et = lr));
            } else if (!(
              Ht[1].type === "linePrefix" ||
              Ht[1].type === "blockQuotePrefix" ||
              Ht[1].type === "blockQuotePrefixWhitespace" ||
              Ht[1].type === "blockQuoteMarker" ||
              Ht[1].type === "listItemIndent"
            ))
              break;
          }
          (Zr && (!Et || Zr < Et) && ($t._spread = !0),
            ($t.end = Object.assign({}, Et ? k[Et][1].start : rt[1].end)),
            k.splice(Et || W, 0, ["exit", $t, rt[2]]),
            W++,
            $++);
        }
        if (rt[1].type === "listItemPrefix") {
          const lr = {
            type: "listItem",
            _spread: !1,
            start: Object.assign({}, rt[1].start),
            end: void 0,
          };
          (($t = lr),
            k.splice(W, 0, ["enter", lr, rt[2]]),
            W++,
            $++,
            (Zr = void 0),
            (Xr = !0));
        }
      }
    }
    return ((k[A][1]._spread = xe), $);
  }
  function o(k, A) {
    return $;
    function $(W) {
      (a.call(this, k(W), W), A && A.call(this, W));
    }
  }
  function l() {
    this.stack.push({ type: "fragment", children: [] });
  }
  function a(k, A, $) {
    (this.stack[this.stack.length - 1].children.push(k),
      this.stack.push(k),
      this.tokenStack.push([A, $ || void 0]),
      (k.position = { start: un(A.start), end: void 0 }));
  }
  function s(k) {
    return A;
    function A($) {
      (k && k.call(this, $), u.call(this, $));
    }
  }
  function u(k, A) {
    const $ = this.stack.pop(),
      W = this.tokenStack.pop();
    if (W)
      W[0].type !== k.type &&
        (A ? A.call(this, k, W[0]) : (W[1] || yf).call(this, k, W[0]));
    else
      throw new Error(
        "Cannot close `" +
          k.type +
          "` (" +
          Si({ start: k.start, end: k.end }) +
          "): it’s not open",
      );
    $.position.end = un(k.end);
  }
  function d() {
    return dc(this.stack.pop());
  }
  function c() {
    this.data.expectingFirstListItemValue = !0;
  }
  function f(k) {
    if (this.data.expectingFirstListItemValue) {
      const A = this.stack[this.stack.length - 2];
      ((A.start = Number.parseInt(this.sliceSerialize(k), 10)),
        (this.data.expectingFirstListItemValue = void 0));
    }
  }
  function p() {
    const k = this.resume(),
      A = this.stack[this.stack.length - 1];
    A.lang = k;
  }
  function g() {
    const k = this.resume(),
      A = this.stack[this.stack.length - 1];
    A.meta = k;
  }
  function y() {
    this.data.flowCodeInside ||
      (this.buffer(), (this.data.flowCodeInside = !0));
  }
  function E() {
    const k = this.resume(),
      A = this.stack[this.stack.length - 1];
    ((A.value = k.replace(/^(\r?\n|\r)|(\r?\n|\r)$/g, "")),
      (this.data.flowCodeInside = void 0));
  }
  function h() {
    const k = this.resume(),
      A = this.stack[this.stack.length - 1];
    A.value = k.replace(/(\r?\n|\r)$/g, "");
  }
  function m(k) {
    const A = this.resume(),
      $ = this.stack[this.stack.length - 1];
    (($.label = A), ($.identifier = Ct(this.sliceSerialize(k)).toLowerCase()));
  }
  function b() {
    const k = this.resume(),
      A = this.stack[this.stack.length - 1];
    A.title = k;
  }
  function _() {
    const k = this.resume(),
      A = this.stack[this.stack.length - 1];
    A.url = k;
  }
  function N(k) {
    const A = this.stack[this.stack.length - 1];
    if (!A.depth) {
      const $ = this.sliceSerialize(k).length;
      A.depth = $;
    }
  }
  function x() {
    this.data.setextHeadingSlurpLineEnding = !0;
  }
  function O(k) {
    const A = this.stack[this.stack.length - 1];
    A.depth = this.sliceSerialize(k).codePointAt(0) === 61 ? 1 : 2;
  }
  function I() {
    this.data.setextHeadingSlurpLineEnding = void 0;
  }
  function U(k) {
    const $ = this.stack[this.stack.length - 1].children;
    let W = $[$.length - 1];
    ((!W || W.type !== "text") &&
      ((W = Yr()),
      (W.position = { start: un(k.start), end: void 0 }),
      $.push(W)),
      this.stack.push(W));
  }
  function S(k) {
    const A = this.stack.pop();
    ((A.value += this.sliceSerialize(k)), (A.position.end = un(k.end)));
  }
  function F(k) {
    const A = this.stack[this.stack.length - 1];
    if (this.data.atHardBreak) {
      const $ = A.children[A.children.length - 1];
      (($.position.end = un(k.end)), (this.data.atHardBreak = void 0));
      return;
    }
    !this.data.setextHeadingSlurpLineEnding &&
      t.canContainEols.includes(A.type) &&
      (U.call(this, k), S.call(this, k));
  }
  function L() {
    this.data.atHardBreak = !0;
  }
  function Q() {
    const k = this.resume(),
      A = this.stack[this.stack.length - 1];
    A.value = k;
  }
  function V() {
    const k = this.resume(),
      A = this.stack[this.stack.length - 1];
    A.value = k;
  }
  function G() {
    const k = this.resume(),
      A = this.stack[this.stack.length - 1];
    A.value = k;
  }
  function R() {
    const k = this.stack[this.stack.length - 1];
    if (this.data.inReference) {
      const A = this.data.referenceType || "shortcut";
      ((k.type += "Reference"),
        (k.referenceType = A),
        delete k.url,
        delete k.title);
    } else (delete k.identifier, delete k.label);
    this.data.referenceType = void 0;
  }
  function B() {
    const k = this.stack[this.stack.length - 1];
    if (this.data.inReference) {
      const A = this.data.referenceType || "shortcut";
      ((k.type += "Reference"),
        (k.referenceType = A),
        delete k.url,
        delete k.title);
    } else (delete k.identifier, delete k.label);
    this.data.referenceType = void 0;
  }
  function C(k) {
    const A = this.sliceSerialize(k),
      $ = this.stack[this.stack.length - 2];
    (($.label = J0(A)), ($.identifier = Ct(A).toLowerCase()));
  }
  function M() {
    const k = this.stack[this.stack.length - 1],
      A = this.resume(),
      $ = this.stack[this.stack.length - 1];
    if (((this.data.inReference = !0), $.type === "link")) {
      const W = k.children;
      $.children = W;
    } else $.alt = A;
  }
  function v() {
    const k = this.resume(),
      A = this.stack[this.stack.length - 1];
    A.url = k;
  }
  function H() {
    const k = this.resume(),
      A = this.stack[this.stack.length - 1];
    A.title = k;
  }
  function K() {
    this.data.inReference = void 0;
  }
  function w() {
    this.data.referenceType = "collapsed";
  }
  function ne(k) {
    const A = this.resume(),
      $ = this.stack[this.stack.length - 1];
    (($.label = A),
      ($.identifier = Ct(this.sliceSerialize(k)).toLowerCase()),
      (this.data.referenceType = "full"));
  }
  function pe(k) {
    this.data.characterReferenceType = k.type;
  }
  function oe(k) {
    const A = this.sliceSerialize(k),
      $ = this.data.characterReferenceType;
    let W;
    $
      ? ((W = om(A, $ === "characterReferenceMarkerNumeric" ? 10 : 16)),
        (this.data.characterReferenceType = void 0))
      : (W = fc(A));
    const X = this.stack[this.stack.length - 1];
    X.value += W;
  }
  function $e(k) {
    const A = this.stack.pop();
    A.position.end = un(k.end);
  }
  function Ye(k) {
    S.call(this, k);
    const A = this.stack[this.stack.length - 1];
    A.url = this.sliceSerialize(k);
  }
  function Rt(k) {
    S.call(this, k);
    const A = this.stack[this.stack.length - 1];
    A.url = "mailto:" + this.sliceSerialize(k);
  }
  function Ot() {
    return { type: "blockquote", children: [] };
  }
  function nn() {
    return { type: "code", lang: null, meta: null, value: "" };
  }
  function qr() {
    return { type: "inlineCode", value: "" };
  }
  function rn() {
    return {
      type: "definition",
      identifier: "",
      label: null,
      title: null,
      url: "",
    };
  }
  function ir() {
    return { type: "emphasis", children: [] };
  }
  function He() {
    return { type: "heading", depth: 0, children: [] };
  }
  function le() {
    return { type: "break" };
  }
  function vt() {
    return { type: "html", value: "" };
  }
  function Y() {
    return { type: "image", title: null, url: "", alt: null };
  }
  function In() {
    return { type: "link", title: null, url: "", children: [] };
  }
  function ke(k) {
    return {
      type: "list",
      ordered: k.type === "listOrdered",
      start: null,
      spread: k._spread,
      children: [],
    };
  }
  function se(k) {
    return { type: "listItem", spread: k._spread, checked: null, children: [] };
  }
  function or() {
    return { type: "paragraph", children: [] };
  }
  function Ut() {
    return { type: "strong", children: [] };
  }
  function Yr() {
    return { type: "text", value: "" };
  }
  function Qr() {
    return { type: "thematicBreak" };
  }
}
function un(e) {
  return { line: e.line, column: e.column, offset: e.offset };
}
function mm(e, t) {
  let n = -1;
  for (; ++n < t.length;) {
    const r = t[n];
    Array.isArray(r) ? mm(e, r) : rk(e, r);
  }
}
function rk(e, t) {
  let n;
  for (n in t)
    if (gm.call(t, n))
      switch (n) {
        case "canContainEols": {
          const r = t[n];
          r && e[n].push(...r);
          break;
        }
        case "transforms": {
          const r = t[n];
          r && e[n].push(...r);
          break;
        }
        case "enter":
        case "exit": {
          const r = t[n];
          r && Object.assign(e[n], r);
          break;
        }
      }
}
function yf(e, t) {
  throw e
    ? new Error(
        "Cannot close `" +
          e.type +
          "` (" +
          Si({ start: e.start, end: e.end }) +
          "): a different token (`" +
          t.type +
          "`, " +
          Si({ start: t.start, end: t.end }) +
          ") is open",
      )
    : new Error(
        "Cannot close document, a token (`" +
          t.type +
          "`, " +
          Si({ start: t.start, end: t.end }) +
          ") is still open",
      );
}
function ik(e) {
  const t = this;
  t.parser = n;
  function n(r) {
    return tk(r, {
      ...t.data("settings"),
      ...e,
      extensions: t.data("micromarkExtensions") || [],
      mdastExtensions: t.data("fromMarkdownExtensions") || [],
    });
  }
}
function ok(e, t) {
  const n = {
    type: "element",
    tagName: "blockquote",
    properties: {},
    children: e.wrap(e.all(t), !0),
  };
  return (e.patch(t, n), e.applyData(t, n));
}
function lk(e, t) {
  const n = { type: "element", tagName: "br", properties: {}, children: [] };
  return (
    e.patch(t, n),
    [
      e.applyData(t, n),
      {
        type: "text",
        value: `
`,
      },
    ]
  );
}
function ak(e, t) {
  const n = t.value
      ? t.value +
        `
`
      : "",
    r = {},
    i = t.lang ? t.lang.split(/\s+/) : [];
  i.length > 0 && (r.className = ["language-" + i[0]]);
  let o = {
    type: "element",
    tagName: "code",
    properties: r,
    children: [{ type: "text", value: n }],
  };
  return (
    t.meta && (o.data = { meta: t.meta }),
    e.patch(t, o),
    (o = e.applyData(t, o)),
    (o = { type: "element", tagName: "pre", properties: {}, children: [o] }),
    e.patch(t, o),
    o
  );
}
function sk(e, t) {
  const n = {
    type: "element",
    tagName: "del",
    properties: {},
    children: e.all(t),
  };
  return (e.patch(t, n), e.applyData(t, n));
}
function uk(e, t) {
  const n = {
    type: "element",
    tagName: "em",
    properties: {},
    children: e.all(t),
  };
  return (e.patch(t, n), e.applyData(t, n));
}
function ck(e, t) {
  const n =
      typeof e.options.clobberPrefix == "string"
        ? e.options.clobberPrefix
        : "user-content-",
    r = String(t.identifier).toUpperCase(),
    i = Vr(r.toLowerCase()),
    o = e.footnoteOrder.indexOf(r);
  let l,
    a = e.footnoteCounts.get(r);
  (a === void 0
    ? ((a = 0), e.footnoteOrder.push(r), (l = e.footnoteOrder.length))
    : (l = o + 1),
    (a += 1),
    e.footnoteCounts.set(r, a));
  const s = {
    type: "element",
    tagName: "a",
    properties: {
      href: "#" + n + "fn-" + i,
      id: n + "fnref-" + i + (a > 1 ? "-" + a : ""),
      dataFootnoteRef: !0,
      ariaDescribedBy: ["footnote-label"],
    },
    children: [{ type: "text", value: String(l) }],
  };
  e.patch(t, s);
  const u = { type: "element", tagName: "sup", properties: {}, children: [s] };
  return (e.patch(t, u), e.applyData(t, u));
}
function dk(e, t) {
  const n = {
    type: "element",
    tagName: "h" + t.depth,
    properties: {},
    children: e.all(t),
  };
  return (e.patch(t, n), e.applyData(t, n));
}
function fk(e, t) {
  if (e.options.allowDangerousHtml) {
    const n = { type: "raw", value: t.value };
    return (e.patch(t, n), e.applyData(t, n));
  }
}
function ym(e, t) {
  const n = t.referenceType;
  let r = "]";
  if (
    (n === "collapsed"
      ? (r += "[]")
      : n === "full" && (r += "[" + (t.label || t.identifier) + "]"),
    t.type === "imageReference")
  )
    return [{ type: "text", value: "![" + t.alt + r }];
  const i = e.all(t),
    o = i[0];
  o && o.type === "text"
    ? (o.value = "[" + o.value)
    : i.unshift({ type: "text", value: "[" });
  const l = i[i.length - 1];
  return (
    l && l.type === "text"
      ? (l.value += r)
      : i.push({ type: "text", value: r }),
    i
  );
}
function pk(e, t) {
  const n = String(t.identifier).toUpperCase(),
    r = e.definitionById.get(n);
  if (!r) return ym(e, t);
  const i = { src: Vr(r.url || ""), alt: t.alt };
  r.title !== null && r.title !== void 0 && (i.title = r.title);
  const o = { type: "element", tagName: "img", properties: i, children: [] };
  return (e.patch(t, o), e.applyData(t, o));
}
function hk(e, t) {
  const n = { src: Vr(t.url) };
  (t.alt !== null && t.alt !== void 0 && (n.alt = t.alt),
    t.title !== null && t.title !== void 0 && (n.title = t.title));
  const r = { type: "element", tagName: "img", properties: n, children: [] };
  return (e.patch(t, r), e.applyData(t, r));
}
function gk(e, t) {
  const n = { type: "text", value: t.value.replace(/\r?\n|\r/g, " ") };
  e.patch(t, n);
  const r = { type: "element", tagName: "code", properties: {}, children: [n] };
  return (e.patch(t, r), e.applyData(t, r));
}
function mk(e, t) {
  const n = String(t.identifier).toUpperCase(),
    r = e.definitionById.get(n);
  if (!r) return ym(e, t);
  const i = { href: Vr(r.url || "") };
  r.title !== null && r.title !== void 0 && (i.title = r.title);
  const o = {
    type: "element",
    tagName: "a",
    properties: i,
    children: e.all(t),
  };
  return (e.patch(t, o), e.applyData(t, o));
}
function yk(e, t) {
  const n = { href: Vr(t.url) };
  t.title !== null && t.title !== void 0 && (n.title = t.title);
  const r = {
    type: "element",
    tagName: "a",
    properties: n,
    children: e.all(t),
  };
  return (e.patch(t, r), e.applyData(t, r));
}
function bk(e, t, n) {
  const r = e.all(t),
    i = n ? vk(n) : bm(t),
    o = {},
    l = [];
  if (typeof t.checked == "boolean") {
    const d = r[0];
    let c;
    (d && d.type === "element" && d.tagName === "p"
      ? (c = d)
      : ((c = { type: "element", tagName: "p", properties: {}, children: [] }),
        r.unshift(c)),
      c.children.length > 0 && c.children.unshift({ type: "text", value: " " }),
      c.children.unshift({
        type: "element",
        tagName: "input",
        properties: { type: "checkbox", checked: t.checked, disabled: !0 },
        children: [],
      }),
      (o.className = ["task-list-item"]));
  }
  let a = -1;
  for (; ++a < r.length;) {
    const d = r[a];
    ((i || a !== 0 || d.type !== "element" || d.tagName !== "p") &&
      l.push({
        type: "text",
        value: `
`,
      }),
      d.type === "element" && d.tagName === "p" && !i
        ? l.push(...d.children)
        : l.push(d));
  }
  const s = r[r.length - 1];
  s &&
    (i || s.type !== "element" || s.tagName !== "p") &&
    l.push({
      type: "text",
      value: `
`,
    });
  const u = { type: "element", tagName: "li", properties: o, children: l };
  return (e.patch(t, u), e.applyData(t, u));
}
function vk(e) {
  let t = !1;
  if (e.type === "list") {
    t = e.spread || !1;
    const n = e.children;
    let r = -1;
    for (; !t && ++r < n.length;) t = bm(n[r]);
  }
  return t;
}
function bm(e) {
  const t = e.spread;
  return t ?? e.children.length > 1;
}
function Ek(e, t) {
  const n = {},
    r = e.all(t);
  let i = -1;
  for (
    typeof t.start == "number" && t.start !== 1 && (n.start = t.start);
    ++i < r.length;
  ) {
    const l = r[i];
    if (
      l.type === "element" &&
      l.tagName === "li" &&
      l.properties &&
      Array.isArray(l.properties.className) &&
      l.properties.className.includes("task-list-item")
    ) {
      n.className = ["contains-task-list"];
      break;
    }
  }
  const o = {
    type: "element",
    tagName: t.ordered ? "ol" : "ul",
    properties: n,
    children: e.wrap(r, !0),
  };
  return (e.patch(t, o), e.applyData(t, o));
}
function wk(e, t) {
  const n = {
    type: "element",
    tagName: "p",
    properties: {},
    children: e.all(t),
  };
  return (e.patch(t, n), e.applyData(t, n));
}
function xk(e, t) {
  const n = { type: "root", children: e.wrap(e.all(t)) };
  return (e.patch(t, n), e.applyData(t, n));
}
function _k(e, t) {
  const n = {
    type: "element",
    tagName: "strong",
    properties: {},
    children: e.all(t),
  };
  return (e.patch(t, n), e.applyData(t, n));
}
function kk(e, t) {
  const n = e.all(t),
    r = n.shift(),
    i = [];
  if (r) {
    const l = {
      type: "element",
      tagName: "thead",
      properties: {},
      children: e.wrap([r], !0),
    };
    (e.patch(t.children[0], l), i.push(l));
  }
  if (n.length > 0) {
    const l = {
        type: "element",
        tagName: "tbody",
        properties: {},
        children: e.wrap(n, !0),
      },
      a = ac(t.children[1]),
      s = Zg(t.children[t.children.length - 1]);
    (a && s && (l.position = { start: a, end: s }), i.push(l));
  }
  const o = {
    type: "element",
    tagName: "table",
    properties: {},
    children: e.wrap(i, !0),
  };
  return (e.patch(t, o), e.applyData(t, o));
}
function Sk(e, t, n) {
  const r = n ? n.children : void 0,
    o = (r ? r.indexOf(t) : 1) === 0 ? "th" : "td",
    l = n && n.type === "table" ? n.align : void 0,
    a = l ? l.length : t.children.length;
  let s = -1;
  const u = [];
  for (; ++s < a;) {
    const c = t.children[s],
      f = {},
      p = l ? l[s] : void 0;
    p && (f.align = p);
    let g = { type: "element", tagName: o, properties: f, children: [] };
    (c && ((g.children = e.all(c)), e.patch(c, g), (g = e.applyData(c, g))),
      u.push(g));
  }
  const d = {
    type: "element",
    tagName: "tr",
    properties: {},
    children: e.wrap(u, !0),
  };
  return (e.patch(t, d), e.applyData(t, d));
}
function Nk(e, t) {
  const n = {
    type: "element",
    tagName: "td",
    properties: {},
    children: e.all(t),
  };
  return (e.patch(t, n), e.applyData(t, n));
}
const bf = 9,
  vf = 32;
function Ck(e) {
  const t = String(e),
    n = /\r?\n|\r/g;
  let r = n.exec(t),
    i = 0;
  const o = [];
  for (; r;)
    (o.push(Ef(t.slice(i, r.index), i > 0, !0), r[0]),
      (i = r.index + r[0].length),
      (r = n.exec(t)));
  return (o.push(Ef(t.slice(i), i > 0, !1)), o.join(""));
}
function Ef(e, t, n) {
  let r = 0,
    i = e.length;
  if (t) {
    let o = e.codePointAt(r);
    for (; o === bf || o === vf;) (r++, (o = e.codePointAt(r)));
  }
  if (n) {
    let o = e.codePointAt(i - 1);
    for (; o === bf || o === vf;) (i--, (o = e.codePointAt(i - 1)));
  }
  return i > r ? e.slice(r, i) : "";
}
function Tk(e, t) {
  const n = { type: "text", value: Ck(String(t.value)) };
  return (e.patch(t, n), e.applyData(t, n));
}
function Ak(e, t) {
  const n = { type: "element", tagName: "hr", properties: {}, children: [] };
  return (e.patch(t, n), e.applyData(t, n));
}
const Rk = {
  blockquote: ok,
  break: lk,
  code: ak,
  delete: sk,
  emphasis: uk,
  footnoteReference: ck,
  heading: dk,
  html: fk,
  imageReference: pk,
  image: hk,
  inlineCode: gk,
  linkReference: mk,
  link: yk,
  listItem: bk,
  list: Ek,
  paragraph: wk,
  root: xk,
  strong: _k,
  table: kk,
  tableCell: Nk,
  tableRow: Sk,
  text: Tk,
  thematicBreak: Ak,
  toml: No,
  yaml: No,
  definition: No,
  footnoteDefinition: No,
};
function No() {}
const vm = -1,
  Zl = 0,
  Ci = 1,
  kl = 2,
  hc = 3,
  gc = 4,
  mc = 5,
  yc = 6,
  Em = 7,
  wm = 8,
  xm = typeof self == "object" ? self : globalThis,
  wf = (e, t) => {
    switch (e) {
      case "Function":
      case "SharedWorker":
      case "Worker":
      case "eval":
      case "setInterval":
      case "setTimeout":
        throw new TypeError("unable to deserialize " + e);
    }
    return new xm[e](t);
  },
  Ok = (e, t) => {
    const n = (i, o) => (e.set(o, i), i),
      r = (i) => {
        if (e.has(i)) return e.get(i);
        const [o, l] = t[i];
        switch (o) {
          case Zl:
          case vm:
            return n(l, i);
          case Ci: {
            const a = n([], i);
            for (const s of l) a.push(r(s));
            return a;
          }
          case kl: {
            const a = n({}, i);
            for (const [s, u] of l) a[r(s)] = r(u);
            return a;
          }
          case hc:
            return n(new Date(l), i);
          case gc: {
            const { source: a, flags: s } = l;
            return n(new RegExp(a, s), i);
          }
          case mc: {
            const a = n(new Map(), i);
            for (const [s, u] of l) a.set(r(s), r(u));
            return a;
          }
          case yc: {
            const a = n(new Set(), i);
            for (const s of l) a.add(r(s));
            return a;
          }
          case Em: {
            const { name: a, message: s } = l;
            return n(typeof xm[a] == "function" ? wf(a, s) : new Error(s), i);
          }
          case wm:
            return n(BigInt(l), i);
          case "BigInt":
            return n(Object(BigInt(l)), i);
          case "ArrayBuffer":
            return n(new Uint8Array(l).buffer, l);
          case "DataView": {
            const { buffer: a } = new Uint8Array(l);
            return n(new DataView(a), l);
          }
        }
        return n(wf(o, l), i);
      };
    return r;
  },
  xf = (e) => Ok(new Map(), e)(0),
  Pn = "",
  { toString: Ik } = {},
  { keys: Mk } = Object,
  ci = (e) => {
    const t = typeof e;
    if (t !== "object" || !e) return [Zl, t];
    const n = Ik.call(e).slice(8, -1);
    switch (n) {
      case "Array":
        return [Ci, Pn];
      case "Object":
        return [kl, Pn];
      case "Date":
        return [hc, Pn];
      case "RegExp":
        return [gc, Pn];
      case "Map":
        return [mc, Pn];
      case "Set":
        return [yc, Pn];
      case "DataView":
        return [Ci, n];
    }
    return n.includes("Array")
      ? [Ci, n]
      : e instanceof Error
        ? [Em, e.name || "Error"]
        : [kl, n];
  },
  Co = ([e, t]) => e === Zl && (t === "function" || t === "symbol"),
  Lk = (e, t, n, r) => {
    const i = (l, a) => {
        const s = r.push(l) - 1;
        return (n.set(a, s), s);
      },
      o = (l) => {
        if (n.has(l)) return n.get(l);
        let [a, s] = ci(l);
        switch (a) {
          case Zl: {
            let d = l;
            switch (s) {
              case "bigint":
                ((a = wm), (d = l.toString()));
                break;
              case "function":
              case "symbol":
                if (e) throw new TypeError("unable to serialize " + s);
                d = null;
                break;
              case "undefined":
                return i([vm], l);
            }
            return i([a, d], l);
          }
          case Ci: {
            if (s) {
              let f = l;
              return (
                s === "DataView"
                  ? (f = new Uint8Array(l.buffer))
                  : s === "ArrayBuffer" && (f = new Uint8Array(l)),
                i([s, [...f]], l)
              );
            }
            const d = [],
              c = i([a, d], l);
            for (const f of l) d.push(o(f));
            return c;
          }
          case kl: {
            if (s)
              switch (s) {
                case "BigInt":
                  return i([s, l.toString()], l);
                case "Boolean":
                case "Number":
                case "String":
                  return i([s, l.valueOf()], l);
              }
            if (t && "toJSON" in l) return o(l.toJSON());
            const d = [],
              c = i([a, d], l);
            for (const f of Mk(l))
              (e || !Co(ci(l[f]))) && d.push([o(f), o(l[f])]);
            return c;
          }
          case hc:
            return i([a, isNaN(l.getTime()) ? Pn : l.toISOString()], l);
          case gc: {
            const { source: d, flags: c } = l;
            return i([a, { source: d, flags: c }], l);
          }
          case mc: {
            const d = [],
              c = i([a, d], l);
            for (const [f, p] of l)
              (e || !(Co(ci(f)) || Co(ci(p)))) && d.push([o(f), o(p)]);
            return c;
          }
          case yc: {
            const d = [],
              c = i([a, d], l);
            for (const f of l) (e || !Co(ci(f))) && d.push(o(f));
            return c;
          }
        }
        const { message: u } = l;
        return i([a, { name: s, message: u }], l);
      };
    return o;
  },
  _f = (e, { json: t, lossy: n } = {}) => {
    const r = [];
    return (Lk(!(t || n), !!t, new Map(), r)(e), r);
  },
  Sl =
    typeof structuredClone == "function"
      ? (e, t) =>
          t && ("json" in t || "lossy" in t) ? xf(_f(e, t)) : structuredClone(e)
      : (e, t) => xf(_f(e, t));
function Dk(e, t) {
  const n = [{ type: "text", value: "↩" }];
  return (
    t > 1 &&
      n.push({
        type: "element",
        tagName: "sup",
        properties: {},
        children: [{ type: "text", value: String(t) }],
      }),
    n
  );
}
function Pk(e, t) {
  return "Back to reference " + (e + 1) + (t > 1 ? "-" + t : "");
}
function zk(e) {
  const t =
      typeof e.options.clobberPrefix == "string"
        ? e.options.clobberPrefix
        : "user-content-",
    n = e.options.footnoteBackContent || Dk,
    r = e.options.footnoteBackLabel || Pk,
    i = e.options.footnoteLabel || "Footnotes",
    o = e.options.footnoteLabelTagName || "h2",
    l = e.options.footnoteLabelProperties || { className: ["sr-only"] },
    a = [];
  let s = -1;
  for (; ++s < e.footnoteOrder.length;) {
    const u = e.footnoteById.get(e.footnoteOrder[s]);
    if (!u) continue;
    const d = e.all(u),
      c = String(u.identifier).toUpperCase(),
      f = Vr(c.toLowerCase());
    let p = 0;
    const g = [],
      y = e.footnoteCounts.get(c);
    for (; y !== void 0 && ++p <= y;) {
      g.length > 0 && g.push({ type: "text", value: " " });
      let m = typeof n == "string" ? n : n(s, p);
      (typeof m == "string" && (m = { type: "text", value: m }),
        g.push({
          type: "element",
          tagName: "a",
          properties: {
            href: "#" + t + "fnref-" + f + (p > 1 ? "-" + p : ""),
            dataFootnoteBackref: "",
            ariaLabel: typeof r == "string" ? r : r(s, p),
            className: ["data-footnote-backref"],
          },
          children: Array.isArray(m) ? m : [m],
        }));
    }
    const E = d[d.length - 1];
    if (E && E.type === "element" && E.tagName === "p") {
      const m = E.children[E.children.length - 1];
      (m && m.type === "text"
        ? (m.value += " ")
        : E.children.push({ type: "text", value: " " }),
        E.children.push(...g));
    } else d.push(...g);
    const h = {
      type: "element",
      tagName: "li",
      properties: { id: t + "fn-" + f },
      children: e.wrap(d, !0),
    };
    (e.patch(u, h), a.push(h));
  }
  if (a.length !== 0)
    return {
      type: "element",
      tagName: "section",
      properties: { dataFootnotes: !0, className: ["footnotes"] },
      children: [
        {
          type: "element",
          tagName: o,
          properties: { ...Sl(l), id: "footnote-label" },
          children: [{ type: "text", value: i }],
        },
        {
          type: "text",
          value: `
`,
        },
        {
          type: "element",
          tagName: "ol",
          properties: {},
          children: e.wrap(a, !0),
        },
        {
          type: "text",
          value: `
`,
        },
      ],
    };
}
const lo = function (e) {
  if (e == null) return $k;
  if (typeof e == "function") return Xl(e);
  if (typeof e == "object") return Array.isArray(e) ? Fk(e) : Bk(e);
  if (typeof e == "string") return Uk(e);
  throw new Error("Expected function, string, or object as test");
};
function Fk(e) {
  const t = [];
  let n = -1;
  for (; ++n < e.length;) t[n] = lo(e[n]);
  return Xl(r);
  function r(...i) {
    let o = -1;
    for (; ++o < t.length;) if (t[o].apply(this, i)) return !0;
    return !1;
  }
}
function Bk(e) {
  const t = e;
  return Xl(n);
  function n(r) {
    const i = r;
    let o;
    for (o in e) if (i[o] !== t[o]) return !1;
    return !0;
  }
}
function Uk(e) {
  return Xl(t);
  function t(n) {
    return n && n.type === e;
  }
}
function Xl(e) {
  return t;
  function t(n, r, i) {
    return !!(
      Hk(n) && e.call(this, n, typeof r == "number" ? r : void 0, i || void 0)
    );
  }
}
function $k() {
  return !0;
}
function Hk(e) {
  return e !== null && typeof e == "object" && "type" in e;
}
const _m = [],
  jk = !0,
  Xs = !1,
  Wk = "skip";
function km(e, t, n, r) {
  let i;
  typeof t == "function" && typeof n != "function"
    ? ((r = n), (n = t))
    : (i = t);
  const o = lo(i),
    l = r ? -1 : 1;
  a(e, void 0, [])();
  function a(s, u, d) {
    const c = s && typeof s == "object" ? s : {};
    if (typeof c.type == "string") {
      const p =
        typeof c.tagName == "string"
          ? c.tagName
          : typeof c.name == "string"
            ? c.name
            : void 0;
      Object.defineProperty(f, "name", {
        value: "node (" + (s.type + (p ? "<" + p + ">" : "")) + ")",
      });
    }
    return f;
    function f() {
      let p = _m,
        g,
        y,
        E;
      if (
        (!t || o(s, u, d[d.length - 1] || void 0)) &&
        ((p = Gk(n(s, d))), p[0] === Xs)
      )
        return p;
      if ("children" in s && s.children) {
        const h = s;
        if (h.children && p[0] !== Wk)
          for (
            y = (r ? h.children.length : -1) + l, E = d.concat(h);
            y > -1 && y < h.children.length;
          ) {
            const m = h.children[y];
            if (((g = a(m, y, E)()), g[0] === Xs)) return g;
            y = typeof g[1] == "number" ? g[1] : y + l;
          }
      }
      return p;
    }
  }
}
function Gk(e) {
  return Array.isArray(e)
    ? e
    : typeof e == "number"
      ? [jk, e]
      : e == null
        ? _m
        : [e];
}
function Jl(e, t, n, r) {
  let i, o, l;
  (typeof t == "function" && typeof n != "function"
    ? ((o = void 0), (l = t), (i = n))
    : ((o = t), (l = n), (i = r)),
    km(e, o, a, i));
  function a(s, u) {
    const d = u[u.length - 1],
      c = d ? d.children.indexOf(s) : void 0;
    return l(s, c, d);
  }
}
const Js = {}.hasOwnProperty,
  Kk = {};
function Vk(e, t) {
  const n = t || Kk,
    r = new Map(),
    i = new Map(),
    o = new Map(),
    l = { ...Rk, ...n.handlers },
    a = {
      all: u,
      applyData: Yk,
      definitionById: r,
      footnoteById: i,
      footnoteCounts: o,
      footnoteOrder: [],
      handlers: l,
      one: s,
      options: n,
      patch: qk,
      wrap: Zk,
    };
  return (
    Jl(e, function (d) {
      if (d.type === "definition" || d.type === "footnoteDefinition") {
        const c = d.type === "definition" ? r : i,
          f = String(d.identifier).toUpperCase();
        c.has(f) || c.set(f, d);
      }
    }),
    a
  );
  function s(d, c) {
    const f = d.type,
      p = a.handlers[f];
    if (Js.call(a.handlers, f) && p) return p(a, d, c);
    if (a.options.passThrough && a.options.passThrough.includes(f)) {
      if ("children" in d) {
        const { children: y, ...E } = d,
          h = Sl(E);
        return ((h.children = a.all(d)), h);
      }
      return Sl(d);
    }
    return (a.options.unknownHandler || Qk)(a, d, c);
  }
  function u(d) {
    const c = [];
    if ("children" in d) {
      const f = d.children;
      let p = -1;
      for (; ++p < f.length;) {
        const g = a.one(f[p], d);
        if (g) {
          if (
            p &&
            f[p - 1].type === "break" &&
            (!Array.isArray(g) && g.type === "text" && (g.value = kf(g.value)),
            !Array.isArray(g) && g.type === "element")
          ) {
            const y = g.children[0];
            y && y.type === "text" && (y.value = kf(y.value));
          }
          Array.isArray(g) ? c.push(...g) : c.push(g);
        }
      }
    }
    return c;
  }
}
function qk(e, t) {
  e.position && (t.position = Px(e));
}
function Yk(e, t) {
  let n = t;
  if (e && e.data) {
    const r = e.data.hName,
      i = e.data.hChildren,
      o = e.data.hProperties;
    if (typeof r == "string")
      if (n.type === "element") n.tagName = r;
      else {
        const l = "children" in n ? n.children : [n];
        n = { type: "element", tagName: r, properties: {}, children: l };
      }
    (n.type === "element" && o && Object.assign(n.properties, Sl(o)),
      "children" in n &&
        n.children &&
        i !== null &&
        i !== void 0 &&
        (n.children = i));
  }
  return n;
}
function Qk(e, t) {
  const n = t.data || {},
    r =
      "value" in t && !(Js.call(n, "hProperties") || Js.call(n, "hChildren"))
        ? { type: "text", value: t.value }
        : {
            type: "element",
            tagName: "div",
            properties: {},
            children: e.all(t),
          };
  return (e.patch(t, r), e.applyData(t, r));
}
function Zk(e, t) {
  const n = [];
  let r = -1;
  for (
    t &&
    n.push({
      type: "text",
      value: `
`,
    });
    ++r < e.length;
  )
    (r &&
      n.push({
        type: "text",
        value: `
`,
      }),
      n.push(e[r]));
  return (
    t &&
      e.length > 0 &&
      n.push({
        type: "text",
        value: `
`,
      }),
    n
  );
}
function kf(e) {
  let t = 0,
    n = e.charCodeAt(t);
  for (; n === 9 || n === 32;) (t++, (n = e.charCodeAt(t)));
  return e.slice(t);
}
function Sf(e, t) {
  const n = Vk(e, t),
    r = n.one(e, void 0),
    i = zk(n),
    o = Array.isArray(r)
      ? { type: "root", children: r }
      : r || { type: "root", children: [] };
  return (
    i &&
      o.children.push(
        {
          type: "text",
          value: `
`,
        },
        i,
      ),
    o
  );
}
function Xk(e, t) {
  return e && "run" in e
    ? async function (n, r) {
        const i = Sf(n, { file: r, ...t });
        await e.run(i, r);
      }
    : function (n, r) {
        return Sf(n, { file: r, ...(e || t) });
      };
}
function Nf(e) {
  if (e) throw e;
}
var Qo = Object.prototype.hasOwnProperty,
  Sm = Object.prototype.toString,
  Cf = Object.defineProperty,
  Tf = Object.getOwnPropertyDescriptor,
  Af = function (t) {
    return typeof Array.isArray == "function"
      ? Array.isArray(t)
      : Sm.call(t) === "[object Array]";
  },
  Rf = function (t) {
    if (!t || Sm.call(t) !== "[object Object]") return !1;
    var n = Qo.call(t, "constructor"),
      r =
        t.constructor &&
        t.constructor.prototype &&
        Qo.call(t.constructor.prototype, "isPrototypeOf");
    if (t.constructor && !n && !r) return !1;
    var i;
    for (i in t);
    return typeof i > "u" || Qo.call(t, i);
  },
  Of = function (t, n) {
    Cf && n.name === "__proto__"
      ? Cf(t, n.name, {
          enumerable: !0,
          configurable: !0,
          value: n.newValue,
          writable: !0,
        })
      : (t[n.name] = n.newValue);
  },
  If = function (t, n) {
    if (n === "__proto__")
      if (Qo.call(t, n)) {
        if (Tf) return Tf(t, n).value;
      } else return;
    return t[n];
  },
  Jk = function e() {
    var t,
      n,
      r,
      i,
      o,
      l,
      a = arguments[0],
      s = 1,
      u = arguments.length,
      d = !1;
    for (
      typeof a == "boolean" && ((d = a), (a = arguments[1] || {}), (s = 2)),
        (a == null || (typeof a != "object" && typeof a != "function")) &&
          (a = {});
      s < u;
      ++s
    )
      if (((t = arguments[s]), t != null))
        for (n in t)
          ((r = If(a, n)),
            (i = If(t, n)),
            a !== i &&
              (d && i && (Rf(i) || (o = Af(i)))
                ? (o
                    ? ((o = !1), (l = r && Af(r) ? r : []))
                    : (l = r && Rf(r) ? r : {}),
                  Of(a, { name: n, newValue: e(d, l, i) }))
                : typeof i < "u" && Of(a, { name: n, newValue: i })));
    return a;
  };
const Ma = Rl(Jk);
function eu(e) {
  if (typeof e != "object" || e === null) return !1;
  const t = Object.getPrototypeOf(e);
  return (
    (t === null ||
      t === Object.prototype ||
      Object.getPrototypeOf(t) === null) &&
    !(Symbol.toStringTag in e) &&
    !(Symbol.iterator in e)
  );
}
function eS() {
  const e = [],
    t = { run: n, use: r };
  return t;
  function n(...i) {
    let o = -1;
    const l = i.pop();
    if (typeof l != "function")
      throw new TypeError("Expected function as last argument, not " + l);
    a(null, ...i);
    function a(s, ...u) {
      const d = e[++o];
      let c = -1;
      if (s) {
        l(s);
        return;
      }
      for (; ++c < i.length;)
        (u[c] === null || u[c] === void 0) && (u[c] = i[c]);
      ((i = u), d ? tS(d, a)(...u) : l(null, ...u));
    }
  }
  function r(i) {
    if (typeof i != "function")
      throw new TypeError("Expected `middelware` to be a function, not " + i);
    return (e.push(i), t);
  }
}
function tS(e, t) {
  let n;
  return r;
  function r(...l) {
    const a = e.length > l.length;
    let s;
    a && l.push(i);
    try {
      s = e.apply(this, l);
    } catch (u) {
      const d = u;
      if (a && n) throw d;
      return i(d);
    }
    a ||
      (s && s.then && typeof s.then == "function"
        ? s.then(o, i)
        : s instanceof Error
          ? i(s)
          : o(s));
  }
  function i(l, ...a) {
    n || ((n = !0), t(l, ...a));
  }
  function o(l) {
    i(null, l);
  }
}
const Dt = { basename: nS, dirname: rS, extname: iS, join: oS, sep: "/" };
function nS(e, t) {
  if (t !== void 0 && typeof t != "string")
    throw new TypeError('"ext" argument must be a string');
  ao(e);
  let n = 0,
    r = -1,
    i = e.length,
    o;
  if (t === void 0 || t.length === 0 || t.length > e.length) {
    for (; i--;)
      if (e.codePointAt(i) === 47) {
        if (o) {
          n = i + 1;
          break;
        }
      } else r < 0 && ((o = !0), (r = i + 1));
    return r < 0 ? "" : e.slice(n, r);
  }
  if (t === e) return "";
  let l = -1,
    a = t.length - 1;
  for (; i--;)
    if (e.codePointAt(i) === 47) {
      if (o) {
        n = i + 1;
        break;
      }
    } else
      (l < 0 && ((o = !0), (l = i + 1)),
        a > -1 &&
          (e.codePointAt(i) === t.codePointAt(a--)
            ? a < 0 && (r = i)
            : ((a = -1), (r = l))));
  return (n === r ? (r = l) : r < 0 && (r = e.length), e.slice(n, r));
}
function rS(e) {
  if ((ao(e), e.length === 0)) return ".";
  let t = -1,
    n = e.length,
    r;
  for (; --n;)
    if (e.codePointAt(n) === 47) {
      if (r) {
        t = n;
        break;
      }
    } else r || (r = !0);
  return t < 0
    ? e.codePointAt(0) === 47
      ? "/"
      : "."
    : t === 1 && e.codePointAt(0) === 47
      ? "//"
      : e.slice(0, t);
}
function iS(e) {
  ao(e);
  let t = e.length,
    n = -1,
    r = 0,
    i = -1,
    o = 0,
    l;
  for (; t--;) {
    const a = e.codePointAt(t);
    if (a === 47) {
      if (l) {
        r = t + 1;
        break;
      }
      continue;
    }
    (n < 0 && ((l = !0), (n = t + 1)),
      a === 46 ? (i < 0 ? (i = t) : o !== 1 && (o = 1)) : i > -1 && (o = -1));
  }
  return i < 0 || n < 0 || o === 0 || (o === 1 && i === n - 1 && i === r + 1)
    ? ""
    : e.slice(i, n);
}
function oS(...e) {
  let t = -1,
    n;
  for (; ++t < e.length;)
    (ao(e[t]), e[t] && (n = n === void 0 ? e[t] : n + "/" + e[t]));
  return n === void 0 ? "." : lS(n);
}
function lS(e) {
  ao(e);
  const t = e.codePointAt(0) === 47;
  let n = aS(e, !t);
  return (
    n.length === 0 && !t && (n = "."),
    n.length > 0 && e.codePointAt(e.length - 1) === 47 && (n += "/"),
    t ? "/" + n : n
  );
}
function aS(e, t) {
  let n = "",
    r = 0,
    i = -1,
    o = 0,
    l = -1,
    a,
    s;
  for (; ++l <= e.length;) {
    if (l < e.length) a = e.codePointAt(l);
    else {
      if (a === 47) break;
      a = 47;
    }
    if (a === 47) {
      if (!(i === l - 1 || o === 1))
        if (i !== l - 1 && o === 2) {
          if (
            n.length < 2 ||
            r !== 2 ||
            n.codePointAt(n.length - 1) !== 46 ||
            n.codePointAt(n.length - 2) !== 46
          ) {
            if (n.length > 2) {
              if (((s = n.lastIndexOf("/")), s !== n.length - 1)) {
                (s < 0
                  ? ((n = ""), (r = 0))
                  : ((n = n.slice(0, s)),
                    (r = n.length - 1 - n.lastIndexOf("/"))),
                  (i = l),
                  (o = 0));
                continue;
              }
            } else if (n.length > 0) {
              ((n = ""), (r = 0), (i = l), (o = 0));
              continue;
            }
          }
          t && ((n = n.length > 0 ? n + "/.." : ".."), (r = 2));
        } else
          (n.length > 0
            ? (n += "/" + e.slice(i + 1, l))
            : (n = e.slice(i + 1, l)),
            (r = l - i - 1));
      ((i = l), (o = 0));
    } else a === 46 && o > -1 ? o++ : (o = -1);
  }
  return n;
}
function ao(e) {
  if (typeof e != "string")
    throw new TypeError("Path must be a string. Received " + JSON.stringify(e));
}
const sS = { cwd: uS };
function uS() {
  return "/";
}
function tu(e) {
  return !!(
    e !== null &&
    typeof e == "object" &&
    "href" in e &&
    e.href &&
    "protocol" in e &&
    e.protocol &&
    e.auth === void 0
  );
}
function cS(e) {
  if (typeof e == "string") e = new URL(e);
  else if (!tu(e)) {
    const t = new TypeError(
      'The "path" argument must be of type string or an instance of URL. Received `' +
        e +
        "`",
    );
    throw ((t.code = "ERR_INVALID_ARG_TYPE"), t);
  }
  if (e.protocol !== "file:") {
    const t = new TypeError("The URL must be of scheme file");
    throw ((t.code = "ERR_INVALID_URL_SCHEME"), t);
  }
  return dS(e);
}
function dS(e) {
  if (e.hostname !== "") {
    const r = new TypeError(
      'File URL host must be "localhost" or empty on darwin',
    );
    throw ((r.code = "ERR_INVALID_FILE_URL_HOST"), r);
  }
  const t = e.pathname;
  let n = -1;
  for (; ++n < t.length;)
    if (t.codePointAt(n) === 37 && t.codePointAt(n + 1) === 50) {
      const r = t.codePointAt(n + 2);
      if (r === 70 || r === 102) {
        const i = new TypeError(
          "File URL path must not include encoded / characters",
        );
        throw ((i.code = "ERR_INVALID_FILE_URL_PATH"), i);
      }
    }
  return decodeURIComponent(t);
}
const La = ["history", "path", "basename", "stem", "extname", "dirname"];
class Nm {
  constructor(t) {
    let n;
    (t
      ? tu(t)
        ? (n = { path: t })
        : typeof t == "string" || fS(t)
          ? (n = { value: t })
          : (n = t)
      : (n = {}),
      (this.cwd = "cwd" in n ? "" : sS.cwd()),
      (this.data = {}),
      (this.history = []),
      (this.messages = []),
      this.value,
      this.map,
      this.result,
      this.stored);
    let r = -1;
    for (; ++r < La.length;) {
      const o = La[r];
      o in n &&
        n[o] !== void 0 &&
        n[o] !== null &&
        (this[o] = o === "history" ? [...n[o]] : n[o]);
    }
    let i;
    for (i in n) La.includes(i) || (this[i] = n[i]);
  }
  get basename() {
    return typeof this.path == "string" ? Dt.basename(this.path) : void 0;
  }
  set basename(t) {
    (Pa(t, "basename"),
      Da(t, "basename"),
      (this.path = Dt.join(this.dirname || "", t)));
  }
  get dirname() {
    return typeof this.path == "string" ? Dt.dirname(this.path) : void 0;
  }
  set dirname(t) {
    (Mf(this.basename, "dirname"),
      (this.path = Dt.join(t || "", this.basename)));
  }
  get extname() {
    return typeof this.path == "string" ? Dt.extname(this.path) : void 0;
  }
  set extname(t) {
    if ((Da(t, "extname"), Mf(this.dirname, "extname"), t)) {
      if (t.codePointAt(0) !== 46)
        throw new Error("`extname` must start with `.`");
      if (t.includes(".", 1))
        throw new Error("`extname` cannot contain multiple dots");
    }
    this.path = Dt.join(this.dirname, this.stem + (t || ""));
  }
  get path() {
    return this.history[this.history.length - 1];
  }
  set path(t) {
    (tu(t) && (t = cS(t)),
      Pa(t, "path"),
      this.path !== t && this.history.push(t));
  }
  get stem() {
    return typeof this.path == "string"
      ? Dt.basename(this.path, this.extname)
      : void 0;
  }
  set stem(t) {
    (Pa(t, "stem"),
      Da(t, "stem"),
      (this.path = Dt.join(this.dirname || "", t + (this.extname || ""))));
  }
  fail(t, n, r) {
    const i = this.message(t, n, r);
    throw ((i.fatal = !0), i);
  }
  info(t, n, r) {
    const i = this.message(t, n, r);
    return ((i.fatal = void 0), i);
  }
  message(t, n, r) {
    const i = new Ue(t, n, r);
    return (
      this.path && ((i.name = this.path + ":" + i.name), (i.file = this.path)),
      (i.fatal = !1),
      this.messages.push(i),
      i
    );
  }
  toString(t) {
    return this.value === void 0
      ? ""
      : typeof this.value == "string"
        ? this.value
        : new TextDecoder(t || void 0).decode(this.value);
  }
}
function Da(e, t) {
  if (e && e.includes(Dt.sep))
    throw new Error(
      "`" + t + "` cannot be a path: did not expect `" + Dt.sep + "`",
    );
}
function Pa(e, t) {
  if (!e) throw new Error("`" + t + "` cannot be empty");
}
function Mf(e, t) {
  if (!e) throw new Error("Setting `" + t + "` requires `path` to be set too");
}
function fS(e) {
  return !!(
    e &&
    typeof e == "object" &&
    "byteLength" in e &&
    "byteOffset" in e
  );
}
const pS = function (e) {
    const r = this.constructor.prototype,
      i = r[e],
      o = function () {
        return i.apply(o, arguments);
      };
    return (Object.setPrototypeOf(o, r), o);
  },
  hS = {}.hasOwnProperty;
class bc extends pS {
  constructor() {
    (super("copy"),
      (this.Compiler = void 0),
      (this.Parser = void 0),
      (this.attachers = []),
      (this.compiler = void 0),
      (this.freezeIndex = -1),
      (this.frozen = void 0),
      (this.namespace = {}),
      (this.parser = void 0),
      (this.transformers = eS()));
  }
  copy() {
    const t = new bc();
    let n = -1;
    for (; ++n < this.attachers.length;) {
      const r = this.attachers[n];
      t.use(...r);
    }
    return (t.data(Ma(!0, {}, this.namespace)), t);
  }
  data(t, n) {
    return typeof t == "string"
      ? arguments.length === 2
        ? (Ba("data", this.frozen), (this.namespace[t] = n), this)
        : (hS.call(this.namespace, t) && this.namespace[t]) || void 0
      : t
        ? (Ba("data", this.frozen), (this.namespace = t), this)
        : this.namespace;
  }
  freeze() {
    if (this.frozen) return this;
    const t = this;
    for (; ++this.freezeIndex < this.attachers.length;) {
      const [n, ...r] = this.attachers[this.freezeIndex];
      if (r[0] === !1) continue;
      r[0] === !0 && (r[0] = void 0);
      const i = n.call(t, ...r);
      typeof i == "function" && this.transformers.use(i);
    }
    return (
      (this.frozen = !0),
      (this.freezeIndex = Number.POSITIVE_INFINITY),
      this
    );
  }
  parse(t) {
    this.freeze();
    const n = To(t),
      r = this.parser || this.Parser;
    return (za("parse", r), r(String(n), n));
  }
  process(t, n) {
    const r = this;
    return (
      this.freeze(),
      za("process", this.parser || this.Parser),
      Fa("process", this.compiler || this.Compiler),
      n ? i(void 0, n) : new Promise(i)
    );
    function i(o, l) {
      const a = To(t),
        s = r.parse(a);
      r.run(s, a, function (d, c, f) {
        if (d || !c || !f) return u(d);
        const p = c,
          g = r.stringify(p, f);
        (yS(g) ? (f.value = g) : (f.result = g), u(d, f));
      });
      function u(d, c) {
        d || !c ? l(d) : o ? o(c) : n(void 0, c);
      }
    }
  }
  processSync(t) {
    let n = !1,
      r;
    return (
      this.freeze(),
      za("processSync", this.parser || this.Parser),
      Fa("processSync", this.compiler || this.Compiler),
      this.process(t, i),
      Df("processSync", "process", n),
      r
    );
    function i(o, l) {
      ((n = !0), Nf(o), (r = l));
    }
  }
  run(t, n, r) {
    (Lf(t), this.freeze());
    const i = this.transformers;
    return (
      !r && typeof n == "function" && ((r = n), (n = void 0)),
      r ? o(void 0, r) : new Promise(o)
    );
    function o(l, a) {
      const s = To(n);
      i.run(t, s, u);
      function u(d, c, f) {
        const p = c || t;
        d ? a(d) : l ? l(p) : r(void 0, p, f);
      }
    }
  }
  runSync(t, n) {
    let r = !1,
      i;
    return (this.run(t, n, o), Df("runSync", "run", r), i);
    function o(l, a) {
      (Nf(l), (i = a), (r = !0));
    }
  }
  stringify(t, n) {
    this.freeze();
    const r = To(n),
      i = this.compiler || this.Compiler;
    return (Fa("stringify", i), Lf(t), i(t, r));
  }
  use(t, ...n) {
    const r = this.attachers,
      i = this.namespace;
    if ((Ba("use", this.frozen), t != null))
      if (typeof t == "function") s(t, n);
      else if (typeof t == "object") Array.isArray(t) ? a(t) : l(t);
      else throw new TypeError("Expected usable value, not `" + t + "`");
    return this;
    function o(u) {
      if (typeof u == "function") s(u, []);
      else if (typeof u == "object")
        if (Array.isArray(u)) {
          const [d, ...c] = u;
          s(d, c);
        } else l(u);
      else throw new TypeError("Expected usable value, not `" + u + "`");
    }
    function l(u) {
      if (!("plugins" in u) && !("settings" in u))
        throw new Error(
          "Expected usable value but received an empty preset, which is probably a mistake: presets typically come with `plugins` and sometimes with `settings`, but this has neither",
        );
      (a(u.plugins),
        u.settings && (i.settings = Ma(!0, i.settings, u.settings)));
    }
    function a(u) {
      let d = -1;
      if (u != null)
        if (Array.isArray(u))
          for (; ++d < u.length;) {
            const c = u[d];
            o(c);
          }
        else throw new TypeError("Expected a list of plugins, not `" + u + "`");
    }
    function s(u, d) {
      let c = -1,
        f = -1;
      for (; ++c < r.length;)
        if (r[c][0] === u) {
          f = c;
          break;
        }
      if (f === -1) r.push([u, ...d]);
      else if (d.length > 0) {
        let [p, ...g] = d;
        const y = r[f][1];
        (eu(y) && eu(p) && (p = Ma(!0, y, p)), (r[f] = [u, p, ...g]));
      }
    }
  }
}
const gS = new bc().freeze();
function za(e, t) {
  if (typeof t != "function")
    throw new TypeError("Cannot `" + e + "` without `parser`");
}
function Fa(e, t) {
  if (typeof t != "function")
    throw new TypeError("Cannot `" + e + "` without `compiler`");
}
function Ba(e, t) {
  if (t)
    throw new Error(
      "Cannot call `" +
        e +
        "` on a frozen processor.\nCreate a new processor first, by calling it: use `processor()` instead of `processor`.",
    );
}
function Lf(e) {
  if (!eu(e) || typeof e.type != "string")
    throw new TypeError("Expected node, got `" + e + "`");
}
function Df(e, t, n) {
  if (!n)
    throw new Error("`" + e + "` finished async. Use `" + t + "` instead");
}
function To(e) {
  return mS(e) ? e : new Nm(e);
}
function mS(e) {
  return !!(e && typeof e == "object" && "message" in e && "messages" in e);
}
function yS(e) {
  return typeof e == "string" || bS(e);
}
function bS(e) {
  return !!(
    e &&
    typeof e == "object" &&
    "byteLength" in e &&
    "byteOffset" in e
  );
}
const vS = "https://github.com/remarkjs/react-markdown/blob/main/changelog.md",
  Pf = [],
  zf = { allowDangerousHtml: !0 },
  ES = /^(https?|ircs?|mailto|xmpp)$/i,
  wS = [
    { from: "astPlugins", id: "remove-buggy-html-in-markdown-parser" },
    { from: "allowDangerousHtml", id: "remove-buggy-html-in-markdown-parser" },
    {
      from: "allowNode",
      id: "replace-allownode-allowedtypes-and-disallowedtypes",
      to: "allowElement",
    },
    {
      from: "allowedTypes",
      id: "replace-allownode-allowedtypes-and-disallowedtypes",
      to: "allowedElements",
    },
    {
      from: "disallowedTypes",
      id: "replace-allownode-allowedtypes-and-disallowedtypes",
      to: "disallowedElements",
    },
    { from: "escapeHtml", id: "remove-buggy-html-in-markdown-parser" },
    { from: "includeElementIndex", id: "#remove-includeelementindex" },
    {
      from: "includeNodeIndex",
      id: "change-includenodeindex-to-includeelementindex",
    },
    { from: "linkTarget", id: "remove-linktarget" },
    {
      from: "plugins",
      id: "change-plugins-to-remarkplugins",
      to: "remarkPlugins",
    },
    { from: "rawSourcePos", id: "#remove-rawsourcepos" },
    {
      from: "renderers",
      id: "change-renderers-to-components",
      to: "components",
    },
    { from: "source", id: "change-source-to-children", to: "children" },
    { from: "sourcePos", id: "#remove-sourcepos" },
    { from: "transformImageUri", id: "#add-urltransform", to: "urlTransform" },
    { from: "transformLinkUri", id: "#add-urltransform", to: "urlTransform" },
  ];
function xS(e) {
  const t = _S(e),
    n = kS(e);
  return SS(t.runSync(t.parse(n), n), e);
}
function _S(e) {
  const t = e.rehypePlugins || Pf,
    n = e.remarkPlugins || Pf,
    r = e.remarkRehypeOptions ? { ...e.remarkRehypeOptions, ...zf } : zf;
  return gS().use(ik).use(n).use(Xk, r).use(t);
}
function kS(e) {
  const t = e.children || "",
    n = new Nm();
  return (typeof t == "string" && (n.value = t), n);
}
function SS(e, t) {
  const n = t.allowedElements,
    r = t.allowElement,
    i = t.components,
    o = t.disallowedElements,
    l = t.skipHtml,
    a = t.unwrapDisallowed,
    s = t.urlTransform || NS;
  for (const d of wS)
    Object.hasOwn(t, d.from) &&
      ("" +
        d.from +
        (d.to ? "use `" + d.to + "` instead" : "remove it") +
        vS +
        d.id,
      void 0);
  return (
    t.className &&
      (e = {
        type: "element",
        tagName: "div",
        properties: { className: t.className },
        children: e.type === "root" ? e.children : [e],
      }),
    Jl(e, u),
    $x(e, {
      Fragment: T.Fragment,
      components: i,
      ignoreInvalidStyle: !0,
      jsx: T.jsx,
      jsxs: T.jsxs,
      passKeys: !0,
      passNode: !0,
    })
  );
  function u(d, c, f) {
    if (d.type === "raw" && f && typeof c == "number")
      return (
        l
          ? f.children.splice(c, 1)
          : (f.children[c] = { type: "text", value: d.value }),
        c
      );
    if (d.type === "element") {
      let p;
      for (p in Ra)
        if (Object.hasOwn(Ra, p) && Object.hasOwn(d.properties, p)) {
          const g = d.properties[p],
            y = Ra[p];
          (y === null || y.includes(d.tagName)) &&
            (d.properties[p] = s(String(g || ""), p, d));
        }
    }
    if (d.type === "element") {
      let p = n ? !n.includes(d.tagName) : o ? o.includes(d.tagName) : !1;
      if (
        (!p && r && typeof c == "number" && (p = !r(d, c, f)),
        p && f && typeof c == "number")
      )
        return (
          a && d.children
            ? f.children.splice(c, 1, ...d.children)
            : f.children.splice(c, 1),
          c
        );
    }
  }
}
function NS(e) {
  const t = e.indexOf(":"),
    n = e.indexOf("?"),
    r = e.indexOf("#"),
    i = e.indexOf("/");
  return t === -1 ||
    (i !== -1 && t > i) ||
    (n !== -1 && t > n) ||
    (r !== -1 && t > r) ||
    ES.test(e.slice(0, t))
    ? e
    : "";
}
function Ff(e, t) {
  const n = String(e);
  if (typeof t != "string") throw new TypeError("Expected character");
  let r = 0,
    i = n.indexOf(t);
  for (; i !== -1;) (r++, (i = n.indexOf(t, i + t.length)));
  return r;
}
function CS(e) {
  if (typeof e != "string") throw new TypeError("Expected a string");
  return e.replace(/[|\\{}()[\]^$+*?.]/g, "\\$&").replace(/-/g, "\\x2d");
}
function TS(e, t, n) {
  const i = lo((n || {}).ignore || []),
    o = AS(t);
  let l = -1;
  for (; ++l < o.length;) km(e, "text", a);
  function a(u, d) {
    let c = -1,
      f;
    for (; ++c < d.length;) {
      const p = d[c],
        g = f ? f.children : void 0;
      if (i(p, g ? g.indexOf(p) : void 0, f)) return;
      f = p;
    }
    if (f) return s(u, d);
  }
  function s(u, d) {
    const c = d[d.length - 1],
      f = o[l][0],
      p = o[l][1];
    let g = 0;
    const E = c.children.indexOf(u);
    let h = !1,
      m = [];
    f.lastIndex = 0;
    let b = f.exec(u.value);
    for (; b;) {
      const _ = b.index,
        N = { index: b.index, input: b.input, stack: [...d, u] };
      let x = p(...b, N);
      if (
        (typeof x == "string" &&
          (x = x.length > 0 ? { type: "text", value: x } : void 0),
        x === !1
          ? (f.lastIndex = _ + 1)
          : (g !== _ && m.push({ type: "text", value: u.value.slice(g, _) }),
            Array.isArray(x) ? m.push(...x) : x && m.push(x),
            (g = _ + b[0].length),
            (h = !0)),
        !f.global)
      )
        break;
      b = f.exec(u.value);
    }
    return (
      h
        ? (g < u.value.length &&
            m.push({ type: "text", value: u.value.slice(g) }),
          c.children.splice(E, 1, ...m))
        : (m = [u]),
      E + m.length
    );
  }
}
function AS(e) {
  const t = [];
  if (!Array.isArray(e))
    throw new TypeError("Expected find and replace tuple or list of tuples");
  const n = !e[0] || Array.isArray(e[0]) ? e : [e];
  let r = -1;
  for (; ++r < n.length;) {
    const i = n[r];
    t.push([RS(i[0]), OS(i[1])]);
  }
  return t;
}
function RS(e) {
  return typeof e == "string" ? new RegExp(CS(e), "g") : e;
}
function OS(e) {
  return typeof e == "function"
    ? e
    : function () {
        return e;
      };
}
const Ua = "phrasing",
  $a = ["autolink", "link", "image", "label"];
function IS() {
  return {
    transforms: [BS],
    enter: {
      literalAutolink: LS,
      literalAutolinkEmail: Ha,
      literalAutolinkHttp: Ha,
      literalAutolinkWww: Ha,
    },
    exit: {
      literalAutolink: FS,
      literalAutolinkEmail: zS,
      literalAutolinkHttp: DS,
      literalAutolinkWww: PS,
    },
  };
}
function MS() {
  return {
    unsafe: [
      {
        character: "@",
        before: "[+\\-.\\w]",
        after: "[\\-.\\w]",
        inConstruct: Ua,
        notInConstruct: $a,
      },
      {
        character: ".",
        before: "[Ww]",
        after: "[\\-.\\w]",
        inConstruct: Ua,
        notInConstruct: $a,
      },
      {
        character: ":",
        before: "[ps]",
        after: "\\/",
        inConstruct: Ua,
        notInConstruct: $a,
      },
    ],
  };
}
function LS(e) {
  this.enter({ type: "link", title: null, url: "", children: [] }, e);
}
function Ha(e) {
  this.config.enter.autolinkProtocol.call(this, e);
}
function DS(e) {
  this.config.exit.autolinkProtocol.call(this, e);
}
function PS(e) {
  this.config.exit.data.call(this, e);
  const t = this.stack[this.stack.length - 1];
  (t.type, (t.url = "http://" + this.sliceSerialize(e)));
}
function zS(e) {
  this.config.exit.autolinkEmail.call(this, e);
}
function FS(e) {
  this.exit(e);
}
function BS(e) {
  TS(
    e,
    [
      [/(https?:\/\/|www(?=\.))([-.\w]+)([^ \t\r\n]*)/gi, US],
      [
        new RegExp(
          "(?<=^|\\s|\\p{P}|\\p{S})([-.\\w+]+)@([-\\w]+(?:\\.[-\\w]+)+)",
          "gu",
        ),
        $S,
      ],
    ],
    { ignore: ["link", "linkReference"] },
  );
}
function US(e, t, n, r, i) {
  let o = "";
  if (
    !Cm(i) ||
    (/^w/i.test(t) && ((n = t + n), (t = ""), (o = "http://")), !HS(n))
  )
    return !1;
  const l = jS(n + r);
  if (!l[0]) return !1;
  const a = {
    type: "link",
    title: null,
    url: o + t + l[0],
    children: [{ type: "text", value: t + l[0] }],
  };
  return l[1] ? [a, { type: "text", value: l[1] }] : a;
}
function $S(e, t, n, r) {
  return !Cm(r, !0) || /[-\d_]$/.test(n)
    ? !1
    : {
        type: "link",
        title: null,
        url: "mailto:" + t + "@" + n,
        children: [{ type: "text", value: t + "@" + n }],
      };
}
function HS(e) {
  const t = e.split(".");
  return !(
    t.length < 2 ||
    (t[t.length - 1] &&
      (/_/.test(t[t.length - 1]) || !/[a-zA-Z\d]/.test(t[t.length - 1]))) ||
    (t[t.length - 2] &&
      (/_/.test(t[t.length - 2]) || !/[a-zA-Z\d]/.test(t[t.length - 2])))
  );
}
function jS(e) {
  const t = /[!"&'),.:;<>?\]}]+$/.exec(e);
  if (!t) return [e, void 0];
  e = e.slice(0, t.index);
  let n = t[0],
    r = n.indexOf(")");
  const i = Ff(e, "(");
  let o = Ff(e, ")");
  for (; r !== -1 && i > o;)
    ((e += n.slice(0, r + 1)), (n = n.slice(r + 1)), (r = n.indexOf(")")), o++);
  return [e, n];
}
function Cm(e, t) {
  const n = e.input.charCodeAt(e.index - 1);
  return (e.index === 0 || Zn(n) || Yl(n)) && (!t || n !== 47);
}
Tm.peek = XS;
function WS() {
  this.buffer();
}
function GS(e) {
  this.enter({ type: "footnoteReference", identifier: "", label: "" }, e);
}
function KS() {
  this.buffer();
}
function VS(e) {
  this.enter(
    { type: "footnoteDefinition", identifier: "", label: "", children: [] },
    e,
  );
}
function qS(e) {
  const t = this.resume(),
    n = this.stack[this.stack.length - 1];
  (n.type,
    (n.identifier = Ct(this.sliceSerialize(e)).toLowerCase()),
    (n.label = t));
}
function YS(e) {
  this.exit(e);
}
function QS(e) {
  const t = this.resume(),
    n = this.stack[this.stack.length - 1];
  (n.type,
    (n.identifier = Ct(this.sliceSerialize(e)).toLowerCase()),
    (n.label = t));
}
function ZS(e) {
  this.exit(e);
}
function XS() {
  return "[";
}
function Tm(e, t, n, r) {
  const i = n.createTracker(r);
  let o = i.move("[^");
  const l = n.enter("footnoteReference"),
    a = n.enter("reference");
  return (
    (o += i.move(n.safe(n.associationId(e), { after: "]", before: o }))),
    a(),
    l(),
    (o += i.move("]")),
    o
  );
}
function JS() {
  return {
    enter: {
      gfmFootnoteCallString: WS,
      gfmFootnoteCall: GS,
      gfmFootnoteDefinitionLabelString: KS,
      gfmFootnoteDefinition: VS,
    },
    exit: {
      gfmFootnoteCallString: qS,
      gfmFootnoteCall: YS,
      gfmFootnoteDefinitionLabelString: QS,
      gfmFootnoteDefinition: ZS,
    },
  };
}
function e1(e) {
  let t = !1;
  return (
    e && e.firstLineBlank && (t = !0),
    {
      handlers: { footnoteDefinition: n, footnoteReference: Tm },
      unsafe: [
        { character: "[", inConstruct: ["label", "phrasing", "reference"] },
      ],
    }
  );
  function n(r, i, o, l) {
    const a = o.createTracker(l);
    let s = a.move("[^");
    const u = o.enter("footnoteDefinition"),
      d = o.enter("label");
    return (
      (s += a.move(o.safe(o.associationId(r), { before: s, after: "]" }))),
      d(),
      (s += a.move("]:")),
      r.children &&
        r.children.length > 0 &&
        (a.shift(4),
        (s += a.move(
          (t
            ? `
`
            : " ") +
            o.indentLines(o.containerFlow(r, a.current()), t ? Am : t1),
        ))),
      u(),
      s
    );
  }
}
function t1(e, t, n) {
  return t === 0 ? e : Am(e, t, n);
}
function Am(e, t, n) {
  return (n ? "" : "    ") + e;
}
const n1 = [
  "autolink",
  "destinationLiteral",
  "destinationRaw",
  "reference",
  "titleQuote",
  "titleApostrophe",
];
Rm.peek = a1;
function r1() {
  return {
    canContainEols: ["delete"],
    enter: { strikethrough: o1 },
    exit: { strikethrough: l1 },
  };
}
function i1() {
  return {
    unsafe: [{ character: "~", inConstruct: "phrasing", notInConstruct: n1 }],
    handlers: { delete: Rm },
  };
}
function o1(e) {
  this.enter({ type: "delete", children: [] }, e);
}
function l1(e) {
  this.exit(e);
}
function Rm(e, t, n, r) {
  const i = n.createTracker(r),
    o = n.enter("strikethrough");
  let l = i.move("~~");
  return (
    (l += n.containerPhrasing(e, { ...i.current(), before: l, after: "~" })),
    (l += i.move("~~")),
    o(),
    l
  );
}
function a1() {
  return "~";
}
function s1(e) {
  return e.length;
}
function u1(e, t) {
  const n = t || {},
    r = (n.align || []).concat(),
    i = n.stringLength || s1,
    o = [],
    l = [],
    a = [],
    s = [];
  let u = 0,
    d = -1;
  for (; ++d < e.length;) {
    const y = [],
      E = [];
    let h = -1;
    for (e[d].length > u && (u = e[d].length); ++h < e[d].length;) {
      const m = c1(e[d][h]);
      if (n.alignDelimiters !== !1) {
        const b = i(m);
        ((E[h] = b), (s[h] === void 0 || b > s[h]) && (s[h] = b));
      }
      y.push(m);
    }
    ((l[d] = y), (a[d] = E));
  }
  let c = -1;
  if (typeof r == "object" && "length" in r) for (; ++c < u;) o[c] = Bf(r[c]);
  else {
    const y = Bf(r);
    for (; ++c < u;) o[c] = y;
  }
  c = -1;
  const f = [],
    p = [];
  for (; ++c < u;) {
    const y = o[c];
    let E = "",
      h = "";
    y === 99
      ? ((E = ":"), (h = ":"))
      : y === 108
        ? (E = ":")
        : y === 114 && (h = ":");
    let m =
      n.alignDelimiters === !1 ? 1 : Math.max(1, s[c] - E.length - h.length);
    const b = E + "-".repeat(m) + h;
    (n.alignDelimiters !== !1 &&
      ((m = E.length + m + h.length), m > s[c] && (s[c] = m), (p[c] = m)),
      (f[c] = b));
  }
  (l.splice(1, 0, f), a.splice(1, 0, p), (d = -1));
  const g = [];
  for (; ++d < l.length;) {
    const y = l[d],
      E = a[d];
    c = -1;
    const h = [];
    for (; ++c < u;) {
      const m = y[c] || "";
      let b = "",
        _ = "";
      if (n.alignDelimiters !== !1) {
        const N = s[c] - (E[c] || 0),
          x = o[c];
        x === 114
          ? (b = " ".repeat(N))
          : x === 99
            ? N % 2
              ? ((b = " ".repeat(N / 2 + 0.5)), (_ = " ".repeat(N / 2 - 0.5)))
              : ((b = " ".repeat(N / 2)), (_ = b))
            : (_ = " ".repeat(N));
      }
      (n.delimiterStart !== !1 && !c && h.push("|"),
        n.padding !== !1 &&
          !(n.alignDelimiters === !1 && m === "") &&
          (n.delimiterStart !== !1 || c) &&
          h.push(" "),
        n.alignDelimiters !== !1 && h.push(b),
        h.push(m),
        n.alignDelimiters !== !1 && h.push(_),
        n.padding !== !1 && h.push(" "),
        (n.delimiterEnd !== !1 || c !== u - 1) && h.push("|"));
    }
    g.push(n.delimiterEnd === !1 ? h.join("").replace(/ +$/, "") : h.join(""));
  }
  return g.join(`
`);
}
function c1(e) {
  return e == null ? "" : String(e);
}
function Bf(e) {
  const t = typeof e == "string" ? e.codePointAt(0) : 0;
  return t === 67 || t === 99
    ? 99
    : t === 76 || t === 108
      ? 108
      : t === 82 || t === 114
        ? 114
        : 0;
}
function d1(e, t, n, r) {
  const i = n.enter("blockquote"),
    o = n.createTracker(r);
  (o.move("> "), o.shift(2));
  const l = n.indentLines(n.containerFlow(e, o.current()), f1);
  return (i(), l);
}
function f1(e, t, n) {
  return ">" + (n ? "" : " ") + e;
}
function p1(e, t) {
  return Uf(e, t.inConstruct, !0) && !Uf(e, t.notInConstruct, !1);
}
function Uf(e, t, n) {
  if ((typeof t == "string" && (t = [t]), !t || t.length === 0)) return n;
  let r = -1;
  for (; ++r < t.length;) if (e.includes(t[r])) return !0;
  return !1;
}
function $f(e, t, n, r) {
  let i = -1;
  for (; ++i < n.unsafe.length;)
    if (
      n.unsafe[i].character ===
        `
` &&
      p1(n.stack, n.unsafe[i])
    )
      return /[ \t]/.test(r.before) ? "" : " ";
  return `\\
`;
}
function h1(e, t) {
  const n = String(e);
  let r = n.indexOf(t),
    i = r,
    o = 0,
    l = 0;
  if (typeof t != "string") throw new TypeError("Expected substring");
  for (; r !== -1;)
    (r === i ? ++o > l && (l = o) : (o = 1),
      (i = r + t.length),
      (r = n.indexOf(t, i)));
  return l;
}
function g1(e, t) {
  return !!(
    t.options.fences === !1 &&
    e.value &&
    !e.lang &&
    /[^ \r\n]/.test(e.value) &&
    !/^[\t ]*(?:[\r\n]|$)|(?:^|[\r\n])[\t ]*$/.test(e.value)
  );
}
function m1(e) {
  const t = e.options.fence || "`";
  if (t !== "`" && t !== "~")
    throw new Error(
      "Cannot serialize code with `" +
        t +
        "` for `options.fence`, expected `` ` `` or `~`",
    );
  return t;
}
function y1(e, t, n, r) {
  const i = m1(n),
    o = e.value || "",
    l = i === "`" ? "GraveAccent" : "Tilde";
  if (g1(e, n)) {
    const c = n.enter("codeIndented"),
      f = n.indentLines(o, b1);
    return (c(), f);
  }
  const a = n.createTracker(r),
    s = i.repeat(Math.max(h1(o, i) + 1, 3)),
    u = n.enter("codeFenced");
  let d = a.move(s);
  if (e.lang) {
    const c = n.enter(`codeFencedLang${l}`);
    ((d += a.move(
      n.safe(e.lang, { before: d, after: " ", encode: ["`"], ...a.current() }),
    )),
      c());
  }
  if (e.lang && e.meta) {
    const c = n.enter(`codeFencedMeta${l}`);
    ((d += a.move(" ")),
      (d += a.move(
        n.safe(e.meta, {
          before: d,
          after: `
`,
          encode: ["`"],
          ...a.current(),
        }),
      )),
      c());
  }
  return (
    (d += a.move(`
`)),
    o &&
      (d += a.move(
        o +
          `
`,
      )),
    (d += a.move(s)),
    u(),
    d
  );
}
function b1(e, t, n) {
  return (n ? "" : "    ") + e;
}
function vc(e) {
  const t = e.options.quote || '"';
  if (t !== '"' && t !== "'")
    throw new Error(
      "Cannot serialize title with `" +
        t +
        "` for `options.quote`, expected `\"`, or `'`",
    );
  return t;
}
function v1(e, t, n, r) {
  const i = vc(n),
    o = i === '"' ? "Quote" : "Apostrophe",
    l = n.enter("definition");
  let a = n.enter("label");
  const s = n.createTracker(r);
  let u = s.move("[");
  return (
    (u += s.move(
      n.safe(n.associationId(e), { before: u, after: "]", ...s.current() }),
    )),
    (u += s.move("]: ")),
    a(),
    !e.url || /[\0- \u007F]/.test(e.url)
      ? ((a = n.enter("destinationLiteral")),
        (u += s.move("<")),
        (u += s.move(n.safe(e.url, { before: u, after: ">", ...s.current() }))),
        (u += s.move(">")))
      : ((a = n.enter("destinationRaw")),
        (u += s.move(
          n.safe(e.url, {
            before: u,
            after: e.title
              ? " "
              : `
`,
            ...s.current(),
          }),
        ))),
    a(),
    e.title &&
      ((a = n.enter(`title${o}`)),
      (u += s.move(" " + i)),
      (u += s.move(n.safe(e.title, { before: u, after: i, ...s.current() }))),
      (u += s.move(i)),
      a()),
    l(),
    u
  );
}
function E1(e) {
  const t = e.options.emphasis || "*";
  if (t !== "*" && t !== "_")
    throw new Error(
      "Cannot serialize emphasis with `" +
        t +
        "` for `options.emphasis`, expected `*`, or `_`",
    );
  return t;
}
function qi(e) {
  return "&#x" + e.toString(16).toUpperCase() + ";";
}
function Nl(e, t, n) {
  const r = Br(e),
    i = Br(t);
  return r === void 0
    ? i === void 0
      ? n === "_"
        ? { inside: !0, outside: !0 }
        : { inside: !1, outside: !1 }
      : i === 1
        ? { inside: !0, outside: !0 }
        : { inside: !1, outside: !0 }
    : r === 1
      ? i === void 0
        ? { inside: !1, outside: !1 }
        : i === 1
          ? { inside: !0, outside: !0 }
          : { inside: !1, outside: !1 }
      : i === void 0
        ? { inside: !1, outside: !1 }
        : i === 1
          ? { inside: !0, outside: !1 }
          : { inside: !1, outside: !1 };
}
Om.peek = w1;
function Om(e, t, n, r) {
  const i = E1(n),
    o = n.enter("emphasis"),
    l = n.createTracker(r),
    a = l.move(i);
  let s = l.move(
    n.containerPhrasing(e, { after: i, before: a, ...l.current() }),
  );
  const u = s.charCodeAt(0),
    d = Nl(r.before.charCodeAt(r.before.length - 1), u, i);
  d.inside && (s = qi(u) + s.slice(1));
  const c = s.charCodeAt(s.length - 1),
    f = Nl(r.after.charCodeAt(0), c, i);
  f.inside && (s = s.slice(0, -1) + qi(c));
  const p = l.move(i);
  return (
    o(),
    (n.attentionEncodeSurroundingInfo = {
      after: f.outside,
      before: d.outside,
    }),
    a + s + p
  );
}
function w1(e, t, n) {
  return n.options.emphasis || "*";
}
function x1(e, t) {
  let n = !1;
  return (
    Jl(e, function (r) {
      if (("value" in r && /\r?\n|\r/.test(r.value)) || r.type === "break")
        return ((n = !0), Xs);
    }),
    !!((!e.depth || e.depth < 3) && dc(e) && (t.options.setext || n))
  );
}
function _1(e, t, n, r) {
  const i = Math.max(Math.min(6, e.depth || 1), 1),
    o = n.createTracker(r);
  if (x1(e, n)) {
    const d = n.enter("headingSetext"),
      c = n.enter("phrasing"),
      f = n.containerPhrasing(e, {
        ...o.current(),
        before: `
`,
        after: `
`,
      });
    return (
      c(),
      d(),
      f +
        `
` +
        (i === 1 ? "=" : "-").repeat(
          f.length -
            (Math.max(
              f.lastIndexOf("\r"),
              f.lastIndexOf(`
`),
            ) +
              1),
        )
    );
  }
  const l = "#".repeat(i),
    a = n.enter("headingAtx"),
    s = n.enter("phrasing");
  o.move(l + " ");
  let u = n.containerPhrasing(e, {
    before: "# ",
    after: `
`,
    ...o.current(),
  });
  return (
    /^[\t ]/.test(u) && (u = qi(u.charCodeAt(0)) + u.slice(1)),
    (u = u ? l + " " + u : l),
    n.options.closeAtx && (u += " " + l),
    s(),
    a(),
    u
  );
}
Im.peek = k1;
function Im(e) {
  return e.value || "";
}
function k1() {
  return "<";
}
Mm.peek = S1;
function Mm(e, t, n, r) {
  const i = vc(n),
    o = i === '"' ? "Quote" : "Apostrophe",
    l = n.enter("image");
  let a = n.enter("label");
  const s = n.createTracker(r);
  let u = s.move("![");
  return (
    (u += s.move(n.safe(e.alt, { before: u, after: "]", ...s.current() }))),
    (u += s.move("](")),
    a(),
    (!e.url && e.title) || /[\0- \u007F]/.test(e.url)
      ? ((a = n.enter("destinationLiteral")),
        (u += s.move("<")),
        (u += s.move(n.safe(e.url, { before: u, after: ">", ...s.current() }))),
        (u += s.move(">")))
      : ((a = n.enter("destinationRaw")),
        (u += s.move(
          n.safe(e.url, {
            before: u,
            after: e.title ? " " : ")",
            ...s.current(),
          }),
        ))),
    a(),
    e.title &&
      ((a = n.enter(`title${o}`)),
      (u += s.move(" " + i)),
      (u += s.move(n.safe(e.title, { before: u, after: i, ...s.current() }))),
      (u += s.move(i)),
      a()),
    (u += s.move(")")),
    l(),
    u
  );
}
function S1() {
  return "!";
}
Lm.peek = N1;
function Lm(e, t, n, r) {
  const i = e.referenceType,
    o = n.enter("imageReference");
  let l = n.enter("label");
  const a = n.createTracker(r);
  let s = a.move("![");
  const u = n.safe(e.alt, { before: s, after: "]", ...a.current() });
  ((s += a.move(u + "][")), l());
  const d = n.stack;
  ((n.stack = []), (l = n.enter("reference")));
  const c = n.safe(n.associationId(e), {
    before: s,
    after: "]",
    ...a.current(),
  });
  return (
    l(),
    (n.stack = d),
    o(),
    i === "full" || !u || u !== c
      ? (s += a.move(c + "]"))
      : i === "shortcut"
        ? (s = s.slice(0, -1))
        : (s += a.move("]")),
    s
  );
}
function N1() {
  return "!";
}
Dm.peek = C1;
function Dm(e, t, n) {
  let r = e.value || "",
    i = "`",
    o = -1;
  for (; new RegExp("(^|[^`])" + i + "([^`]|$)").test(r);) i += "`";
  for (
    /[^ \r\n]/.test(r) &&
    ((/^[ \r\n]/.test(r) && /[ \r\n]$/.test(r)) || /^`|`$/.test(r)) &&
    (r = " " + r + " ");
    ++o < n.unsafe.length;
  ) {
    const l = n.unsafe[o],
      a = n.compilePattern(l);
    let s;
    if (l.atBreak)
      for (; (s = a.exec(r));) {
        let u = s.index;
        (r.charCodeAt(u) === 10 && r.charCodeAt(u - 1) === 13 && u--,
          (r = r.slice(0, u) + " " + r.slice(s.index + 1)));
      }
  }
  return i + r + i;
}
function C1() {
  return "`";
}
function Pm(e, t) {
  const n = dc(e);
  return !!(
    !t.options.resourceLink &&
    e.url &&
    !e.title &&
    e.children &&
    e.children.length === 1 &&
    e.children[0].type === "text" &&
    (n === e.url || "mailto:" + n === e.url) &&
    /^[a-z][a-z+.-]+:/i.test(e.url) &&
    !/[\0- <>\u007F]/.test(e.url)
  );
}
zm.peek = T1;
function zm(e, t, n, r) {
  const i = vc(n),
    o = i === '"' ? "Quote" : "Apostrophe",
    l = n.createTracker(r);
  let a, s;
  if (Pm(e, n)) {
    const d = n.stack;
    ((n.stack = []), (a = n.enter("autolink")));
    let c = l.move("<");
    return (
      (c += l.move(
        n.containerPhrasing(e, { before: c, after: ">", ...l.current() }),
      )),
      (c += l.move(">")),
      a(),
      (n.stack = d),
      c
    );
  }
  ((a = n.enter("link")), (s = n.enter("label")));
  let u = l.move("[");
  return (
    (u += l.move(
      n.containerPhrasing(e, { before: u, after: "](", ...l.current() }),
    )),
    (u += l.move("](")),
    s(),
    (!e.url && e.title) || /[\0- \u007F]/.test(e.url)
      ? ((s = n.enter("destinationLiteral")),
        (u += l.move("<")),
        (u += l.move(n.safe(e.url, { before: u, after: ">", ...l.current() }))),
        (u += l.move(">")))
      : ((s = n.enter("destinationRaw")),
        (u += l.move(
          n.safe(e.url, {
            before: u,
            after: e.title ? " " : ")",
            ...l.current(),
          }),
        ))),
    s(),
    e.title &&
      ((s = n.enter(`title${o}`)),
      (u += l.move(" " + i)),
      (u += l.move(n.safe(e.title, { before: u, after: i, ...l.current() }))),
      (u += l.move(i)),
      s()),
    (u += l.move(")")),
    a(),
    u
  );
}
function T1(e, t, n) {
  return Pm(e, n) ? "<" : "[";
}
Fm.peek = A1;
function Fm(e, t, n, r) {
  const i = e.referenceType,
    o = n.enter("linkReference");
  let l = n.enter("label");
  const a = n.createTracker(r);
  let s = a.move("[");
  const u = n.containerPhrasing(e, { before: s, after: "]", ...a.current() });
  ((s += a.move(u + "][")), l());
  const d = n.stack;
  ((n.stack = []), (l = n.enter("reference")));
  const c = n.safe(n.associationId(e), {
    before: s,
    after: "]",
    ...a.current(),
  });
  return (
    l(),
    (n.stack = d),
    o(),
    i === "full" || !u || u !== c
      ? (s += a.move(c + "]"))
      : i === "shortcut"
        ? (s = s.slice(0, -1))
        : (s += a.move("]")),
    s
  );
}
function A1() {
  return "[";
}
function Ec(e) {
  const t = e.options.bullet || "*";
  if (t !== "*" && t !== "+" && t !== "-")
    throw new Error(
      "Cannot serialize items with `" +
        t +
        "` for `options.bullet`, expected `*`, `+`, or `-`",
    );
  return t;
}
function R1(e) {
  const t = Ec(e),
    n = e.options.bulletOther;
  if (!n) return t === "*" ? "-" : "*";
  if (n !== "*" && n !== "+" && n !== "-")
    throw new Error(
      "Cannot serialize items with `" +
        n +
        "` for `options.bulletOther`, expected `*`, `+`, or `-`",
    );
  if (n === t)
    throw new Error(
      "Expected `bullet` (`" +
        t +
        "`) and `bulletOther` (`" +
        n +
        "`) to be different",
    );
  return n;
}
function O1(e) {
  const t = e.options.bulletOrdered || ".";
  if (t !== "." && t !== ")")
    throw new Error(
      "Cannot serialize items with `" +
        t +
        "` for `options.bulletOrdered`, expected `.` or `)`",
    );
  return t;
}
function Bm(e) {
  const t = e.options.rule || "*";
  if (t !== "*" && t !== "-" && t !== "_")
    throw new Error(
      "Cannot serialize rules with `" +
        t +
        "` for `options.rule`, expected `*`, `-`, or `_`",
    );
  return t;
}
function I1(e, t, n, r) {
  const i = n.enter("list"),
    o = n.bulletCurrent;
  let l = e.ordered ? O1(n) : Ec(n);
  const a = e.ordered ? (l === "." ? ")" : ".") : R1(n);
  let s = t && n.bulletLastUsed ? l === n.bulletLastUsed : !1;
  if (!e.ordered) {
    const d = e.children ? e.children[0] : void 0;
    if (
      ((l === "*" || l === "-") &&
        d &&
        (!d.children || !d.children[0]) &&
        n.stack[n.stack.length - 1] === "list" &&
        n.stack[n.stack.length - 2] === "listItem" &&
        n.stack[n.stack.length - 3] === "list" &&
        n.stack[n.stack.length - 4] === "listItem" &&
        n.indexStack[n.indexStack.length - 1] === 0 &&
        n.indexStack[n.indexStack.length - 2] === 0 &&
        n.indexStack[n.indexStack.length - 3] === 0 &&
        (s = !0),
      Bm(n) === l && d)
    ) {
      let c = -1;
      for (; ++c < e.children.length;) {
        const f = e.children[c];
        if (
          f &&
          f.type === "listItem" &&
          f.children &&
          f.children[0] &&
          f.children[0].type === "thematicBreak"
        ) {
          s = !0;
          break;
        }
      }
    }
  }
  (s && (l = a), (n.bulletCurrent = l));
  const u = n.containerFlow(e, r);
  return ((n.bulletLastUsed = l), (n.bulletCurrent = o), i(), u);
}
function M1(e) {
  const t = e.options.listItemIndent || "one";
  if (t !== "tab" && t !== "one" && t !== "mixed")
    throw new Error(
      "Cannot serialize items with `" +
        t +
        "` for `options.listItemIndent`, expected `tab`, `one`, or `mixed`",
    );
  return t;
}
function L1(e, t, n, r) {
  const i = M1(n);
  let o = n.bulletCurrent || Ec(n);
  t &&
    t.type === "list" &&
    t.ordered &&
    (o =
      (typeof t.start == "number" && t.start > -1 ? t.start : 1) +
      (n.options.incrementListMarker === !1 ? 0 : t.children.indexOf(e)) +
      o);
  let l = o.length + 1;
  (i === "tab" ||
    (i === "mixed" && ((t && t.type === "list" && t.spread) || e.spread))) &&
    (l = Math.ceil(l / 4) * 4);
  const a = n.createTracker(r);
  (a.move(o + " ".repeat(l - o.length)), a.shift(l));
  const s = n.enter("listItem"),
    u = n.indentLines(n.containerFlow(e, a.current()), d);
  return (s(), u);
  function d(c, f, p) {
    return f
      ? (p ? "" : " ".repeat(l)) + c
      : (p ? o : o + " ".repeat(l - o.length)) + c;
  }
}
function D1(e, t, n, r) {
  const i = n.enter("paragraph"),
    o = n.enter("phrasing"),
    l = n.containerPhrasing(e, r);
  return (o(), i(), l);
}
const P1 = lo([
  "break",
  "delete",
  "emphasis",
  "footnote",
  "footnoteReference",
  "image",
  "imageReference",
  "inlineCode",
  "inlineMath",
  "link",
  "linkReference",
  "mdxJsxTextElement",
  "mdxTextExpression",
  "strong",
  "text",
  "textDirective",
]);
function z1(e, t, n, r) {
  return (
    e.children.some(function (l) {
      return P1(l);
    })
      ? n.containerPhrasing
      : n.containerFlow
  ).call(n, e, r);
}
function F1(e) {
  const t = e.options.strong || "*";
  if (t !== "*" && t !== "_")
    throw new Error(
      "Cannot serialize strong with `" +
        t +
        "` for `options.strong`, expected `*`, or `_`",
    );
  return t;
}
Um.peek = B1;
function Um(e, t, n, r) {
  const i = F1(n),
    o = n.enter("strong"),
    l = n.createTracker(r),
    a = l.move(i + i);
  let s = l.move(
    n.containerPhrasing(e, { after: i, before: a, ...l.current() }),
  );
  const u = s.charCodeAt(0),
    d = Nl(r.before.charCodeAt(r.before.length - 1), u, i);
  d.inside && (s = qi(u) + s.slice(1));
  const c = s.charCodeAt(s.length - 1),
    f = Nl(r.after.charCodeAt(0), c, i);
  f.inside && (s = s.slice(0, -1) + qi(c));
  const p = l.move(i + i);
  return (
    o(),
    (n.attentionEncodeSurroundingInfo = {
      after: f.outside,
      before: d.outside,
    }),
    a + s + p
  );
}
function B1(e, t, n) {
  return n.options.strong || "*";
}
function U1(e, t, n, r) {
  return n.safe(e.value, r);
}
function $1(e) {
  const t = e.options.ruleRepetition || 3;
  if (t < 3)
    throw new Error(
      "Cannot serialize rules with repetition `" +
        t +
        "` for `options.ruleRepetition`, expected `3` or more",
    );
  return t;
}
function H1(e, t, n) {
  const r = (Bm(n) + (n.options.ruleSpaces ? " " : "")).repeat($1(n));
  return n.options.ruleSpaces ? r.slice(0, -1) : r;
}
const $m = {
  blockquote: d1,
  break: $f,
  code: y1,
  definition: v1,
  emphasis: Om,
  hardBreak: $f,
  heading: _1,
  html: Im,
  image: Mm,
  imageReference: Lm,
  inlineCode: Dm,
  link: zm,
  linkReference: Fm,
  list: I1,
  listItem: L1,
  paragraph: D1,
  root: z1,
  strong: Um,
  text: U1,
  thematicBreak: H1,
};
function j1() {
  return {
    enter: { table: W1, tableData: Hf, tableHeader: Hf, tableRow: K1 },
    exit: {
      codeText: V1,
      table: G1,
      tableData: ja,
      tableHeader: ja,
      tableRow: ja,
    },
  };
}
function W1(e) {
  const t = e._align;
  (this.enter(
    {
      type: "table",
      align: t.map(function (n) {
        return n === "none" ? null : n;
      }),
      children: [],
    },
    e,
  ),
    (this.data.inTable = !0));
}
function G1(e) {
  (this.exit(e), (this.data.inTable = void 0));
}
function K1(e) {
  this.enter({ type: "tableRow", children: [] }, e);
}
function ja(e) {
  this.exit(e);
}
function Hf(e) {
  this.enter({ type: "tableCell", children: [] }, e);
}
function V1(e) {
  let t = this.resume();
  this.data.inTable && (t = t.replace(/\\([\\|])/g, q1));
  const n = this.stack[this.stack.length - 1];
  (n.type, (n.value = t), this.exit(e));
}
function q1(e, t) {
  return t === "|" ? t : e;
}
function Y1(e) {
  const t = e || {},
    n = t.tableCellPadding,
    r = t.tablePipeAlign,
    i = t.stringLength,
    o = n ? " " : "|";
  return {
    unsafe: [
      { character: "\r", inConstruct: "tableCell" },
      {
        character: `
`,
        inConstruct: "tableCell",
      },
      { atBreak: !0, character: "|", after: "[	 :-]" },
      { character: "|", inConstruct: "tableCell" },
      { atBreak: !0, character: ":", after: "-" },
      { atBreak: !0, character: "-", after: "[:|-]" },
    ],
    handlers: { inlineCode: f, table: l, tableCell: s, tableRow: a },
  };
  function l(p, g, y, E) {
    return u(d(p, y, E), p.align);
  }
  function a(p, g, y, E) {
    const h = c(p, y, E),
      m = u([h]);
    return m.slice(
      0,
      m.indexOf(`
`),
    );
  }
  function s(p, g, y, E) {
    const h = y.enter("tableCell"),
      m = y.enter("phrasing"),
      b = y.containerPhrasing(p, { ...E, before: o, after: o });
    return (m(), h(), b);
  }
  function u(p, g) {
    return u1(p, { align: g, alignDelimiters: r, padding: n, stringLength: i });
  }
  function d(p, g, y) {
    const E = p.children;
    let h = -1;
    const m = [],
      b = g.enter("table");
    for (; ++h < E.length;) m[h] = c(E[h], g, y);
    return (b(), m);
  }
  function c(p, g, y) {
    const E = p.children;
    let h = -1;
    const m = [],
      b = g.enter("tableRow");
    for (; ++h < E.length;) m[h] = s(E[h], p, g, y);
    return (b(), m);
  }
  function f(p, g, y) {
    let E = $m.inlineCode(p, g, y);
    return (y.stack.includes("tableCell") && (E = E.replace(/\|/g, "\\$&")), E);
  }
}
function Q1() {
  return {
    exit: {
      taskListCheckValueChecked: jf,
      taskListCheckValueUnchecked: jf,
      paragraph: X1,
    },
  };
}
function Z1() {
  return {
    unsafe: [{ atBreak: !0, character: "-", after: "[:|-]" }],
    handlers: { listItem: J1 },
  };
}
function jf(e) {
  const t = this.stack[this.stack.length - 2];
  (t.type, (t.checked = e.type === "taskListCheckValueChecked"));
}
function X1(e) {
  const t = this.stack[this.stack.length - 2];
  if (t && t.type === "listItem" && typeof t.checked == "boolean") {
    const n = this.stack[this.stack.length - 1];
    n.type;
    const r = n.children[0];
    if (r && r.type === "text") {
      const i = t.children;
      let o = -1,
        l;
      for (; ++o < i.length;) {
        const a = i[o];
        if (a.type === "paragraph") {
          l = a;
          break;
        }
      }
      l === n &&
        ((r.value = r.value.slice(1)),
        r.value.length === 0
          ? n.children.shift()
          : n.position &&
            r.position &&
            typeof r.position.start.offset == "number" &&
            (r.position.start.column++,
            r.position.start.offset++,
            (n.position.start = Object.assign({}, r.position.start))));
    }
  }
  this.exit(e);
}
function J1(e, t, n, r) {
  const i = e.children[0],
    o = typeof e.checked == "boolean" && i && i.type === "paragraph",
    l = "[" + (e.checked ? "x" : " ") + "] ",
    a = n.createTracker(r);
  o && a.move(l);
  let s = $m.listItem(e, t, n, { ...r, ...a.current() });
  return (o && (s = s.replace(/^(?:[*+-]|\d+\.)([\r\n]| {1,3})/, u)), s);
  function u(d) {
    return d + l;
  }
}
function eN() {
  return [IS(), JS(), r1(), j1(), Q1()];
}
function tN(e) {
  return { extensions: [MS(), e1(e), i1(), Y1(e), Z1()] };
}
const nN = { tokenize: sN, partial: !0 },
  Hm = { tokenize: uN, partial: !0 },
  jm = { tokenize: cN, partial: !0 },
  Wm = { tokenize: dN, partial: !0 },
  rN = { tokenize: fN, partial: !0 },
  Gm = { name: "wwwAutolink", tokenize: lN, previous: Vm },
  Km = { name: "protocolAutolink", tokenize: aN, previous: qm },
  tn = { name: "emailAutolink", tokenize: oN, previous: Ym },
  Bt = {};
function iN() {
  return { text: Bt };
}
let Mn = 48;
for (; Mn < 123;)
  ((Bt[Mn] = tn), Mn++, Mn === 58 ? (Mn = 65) : Mn === 91 && (Mn = 97));
Bt[43] = tn;
Bt[45] = tn;
Bt[46] = tn;
Bt[95] = tn;
Bt[72] = [tn, Km];
Bt[104] = [tn, Km];
Bt[87] = [tn, Gm];
Bt[119] = [tn, Gm];
function oN(e, t, n) {
  const r = this;
  let i, o;
  return l;
  function l(c) {
    return !nu(c) || !Ym.call(r, r.previous) || wc(r.events)
      ? n(c)
      : (e.enter("literalAutolink"), e.enter("literalAutolinkEmail"), a(c));
  }
  function a(c) {
    return nu(c) ? (e.consume(c), a) : c === 64 ? (e.consume(c), s) : n(c);
  }
  function s(c) {
    return c === 46
      ? e.check(rN, d, u)(c)
      : c === 45 || c === 95 || Fe(c)
        ? ((o = !0), e.consume(c), s)
        : d(c);
  }
  function u(c) {
    return (e.consume(c), (i = !0), s);
  }
  function d(c) {
    return o && i && Ge(r.previous)
      ? (e.exit("literalAutolinkEmail"), e.exit("literalAutolink"), t(c))
      : n(c);
  }
}
function lN(e, t, n) {
  const r = this;
  return i;
  function i(l) {
    return (l !== 87 && l !== 119) || !Vm.call(r, r.previous) || wc(r.events)
      ? n(l)
      : (e.enter("literalAutolink"),
        e.enter("literalAutolinkWww"),
        e.check(nN, e.attempt(Hm, e.attempt(jm, o), n), n)(l));
  }
  function o(l) {
    return (e.exit("literalAutolinkWww"), e.exit("literalAutolink"), t(l));
  }
}
function aN(e, t, n) {
  const r = this;
  let i = "",
    o = !1;
  return l;
  function l(c) {
    return (c === 72 || c === 104) && qm.call(r, r.previous) && !wc(r.events)
      ? (e.enter("literalAutolink"),
        e.enter("literalAutolinkHttp"),
        (i += String.fromCodePoint(c)),
        e.consume(c),
        a)
      : n(c);
  }
  function a(c) {
    if (Ge(c) && i.length < 5)
      return ((i += String.fromCodePoint(c)), e.consume(c), a);
    if (c === 58) {
      const f = i.toLowerCase();
      if (f === "http" || f === "https") return (e.consume(c), s);
    }
    return n(c);
  }
  function s(c) {
    return c === 47 ? (e.consume(c), o ? u : ((o = !0), s)) : n(c);
  }
  function u(c) {
    return c === null || _l(c) || de(c) || Zn(c) || Yl(c)
      ? n(c)
      : e.attempt(Hm, e.attempt(jm, d), n)(c);
  }
  function d(c) {
    return (e.exit("literalAutolinkHttp"), e.exit("literalAutolink"), t(c));
  }
}
function sN(e, t, n) {
  let r = 0;
  return i;
  function i(l) {
    return (l === 87 || l === 119) && r < 3
      ? (r++, e.consume(l), i)
      : l === 46 && r === 3
        ? (e.consume(l), o)
        : n(l);
  }
  function o(l) {
    return l === null ? n(l) : t(l);
  }
}
function uN(e, t, n) {
  let r, i, o;
  return l;
  function l(u) {
    return u === 46 || u === 95
      ? e.check(Wm, s, a)(u)
      : u === null || de(u) || Zn(u) || (u !== 45 && Yl(u))
        ? s(u)
        : ((o = !0), e.consume(u), l);
  }
  function a(u) {
    return (u === 95 ? (r = !0) : ((i = r), (r = void 0)), e.consume(u), l);
  }
  function s(u) {
    return i || r || !o ? n(u) : t(u);
  }
}
function cN(e, t) {
  let n = 0,
    r = 0;
  return i;
  function i(l) {
    return l === 40
      ? (n++, e.consume(l), i)
      : l === 41 && r < n
        ? o(l)
        : l === 33 ||
            l === 34 ||
            l === 38 ||
            l === 39 ||
            l === 41 ||
            l === 42 ||
            l === 44 ||
            l === 46 ||
            l === 58 ||
            l === 59 ||
            l === 60 ||
            l === 63 ||
            l === 93 ||
            l === 95 ||
            l === 126
          ? e.check(Wm, t, o)(l)
          : l === null || de(l) || Zn(l)
            ? t(l)
            : (e.consume(l), i);
  }
  function o(l) {
    return (l === 41 && r++, e.consume(l), i);
  }
}
function dN(e, t, n) {
  return r;
  function r(a) {
    return a === 33 ||
      a === 34 ||
      a === 39 ||
      a === 41 ||
      a === 42 ||
      a === 44 ||
      a === 46 ||
      a === 58 ||
      a === 59 ||
      a === 63 ||
      a === 95 ||
      a === 126
      ? (e.consume(a), r)
      : a === 38
        ? (e.consume(a), o)
        : a === 93
          ? (e.consume(a), i)
          : a === 60 || a === null || de(a) || Zn(a)
            ? t(a)
            : n(a);
  }
  function i(a) {
    return a === null || a === 40 || a === 91 || de(a) || Zn(a) ? t(a) : r(a);
  }
  function o(a) {
    return Ge(a) ? l(a) : n(a);
  }
  function l(a) {
    return a === 59 ? (e.consume(a), r) : Ge(a) ? (e.consume(a), l) : n(a);
  }
}
function fN(e, t, n) {
  return r;
  function r(o) {
    return (e.consume(o), i);
  }
  function i(o) {
    return Fe(o) ? n(o) : t(o);
  }
}
function Vm(e) {
  return (
    e === null ||
    e === 40 ||
    e === 42 ||
    e === 95 ||
    e === 91 ||
    e === 93 ||
    e === 126 ||
    de(e)
  );
}
function qm(e) {
  return !Ge(e);
}
function Ym(e) {
  return !(e === 47 || nu(e));
}
function nu(e) {
  return e === 43 || e === 45 || e === 46 || e === 95 || Fe(e);
}
function wc(e) {
  let t = e.length,
    n = !1;
  for (; t--;) {
    const r = e[t][1];
    if ((r.type === "labelLink" || r.type === "labelImage") && !r._balanced) {
      n = !0;
      break;
    }
    if (r._gfmAutolinkLiteralWalkedInto) {
      n = !1;
      break;
    }
  }
  return (
    e.length > 0 &&
      !n &&
      (e[e.length - 1][1]._gfmAutolinkLiteralWalkedInto = !0),
    n
  );
}
const pN = { tokenize: wN, partial: !0 };
function hN() {
  return {
    document: {
      91: {
        name: "gfmFootnoteDefinition",
        tokenize: bN,
        continuation: { tokenize: vN },
        exit: EN,
      },
    },
    text: {
      91: { name: "gfmFootnoteCall", tokenize: yN },
      93: {
        name: "gfmPotentialFootnoteCall",
        add: "after",
        tokenize: gN,
        resolveTo: mN,
      },
    },
  };
}
function gN(e, t, n) {
  const r = this;
  let i = r.events.length;
  const o = r.parser.gfmFootnotes || (r.parser.gfmFootnotes = []);
  let l;
  for (; i--;) {
    const s = r.events[i][1];
    if (s.type === "labelImage") {
      l = s;
      break;
    }
    if (
      s.type === "gfmFootnoteCall" ||
      s.type === "labelLink" ||
      s.type === "label" ||
      s.type === "image" ||
      s.type === "link"
    )
      break;
  }
  return a;
  function a(s) {
    if (!l || !l._balanced) return n(s);
    const u = Ct(r.sliceSerialize({ start: l.end, end: r.now() }));
    return u.codePointAt(0) !== 94 || !o.includes(u.slice(1))
      ? n(s)
      : (e.enter("gfmFootnoteCallLabelMarker"),
        e.consume(s),
        e.exit("gfmFootnoteCallLabelMarker"),
        t(s));
  }
}
function mN(e, t) {
  let n = e.length;
  for (; n--;)
    if (e[n][1].type === "labelImage" && e[n][0] === "enter") {
      e[n][1];
      break;
    }
  ((e[n + 1][1].type = "data"),
    (e[n + 3][1].type = "gfmFootnoteCallLabelMarker"));
  const r = {
      type: "gfmFootnoteCall",
      start: Object.assign({}, e[n + 3][1].start),
      end: Object.assign({}, e[e.length - 1][1].end),
    },
    i = {
      type: "gfmFootnoteCallMarker",
      start: Object.assign({}, e[n + 3][1].end),
      end: Object.assign({}, e[n + 3][1].end),
    };
  (i.end.column++, i.end.offset++, i.end._bufferIndex++);
  const o = {
      type: "gfmFootnoteCallString",
      start: Object.assign({}, i.end),
      end: Object.assign({}, e[e.length - 1][1].start),
    },
    l = {
      type: "chunkString",
      contentType: "string",
      start: Object.assign({}, o.start),
      end: Object.assign({}, o.end),
    },
    a = [
      e[n + 1],
      e[n + 2],
      ["enter", r, t],
      e[n + 3],
      e[n + 4],
      ["enter", i, t],
      ["exit", i, t],
      ["enter", o, t],
      ["enter", l, t],
      ["exit", l, t],
      ["exit", o, t],
      e[e.length - 2],
      e[e.length - 1],
      ["exit", r, t],
    ];
  return (e.splice(n, e.length - n + 1, ...a), e);
}
function yN(e, t, n) {
  const r = this,
    i = r.parser.gfmFootnotes || (r.parser.gfmFootnotes = []);
  let o = 0,
    l;
  return a;
  function a(c) {
    return (
      e.enter("gfmFootnoteCall"),
      e.enter("gfmFootnoteCallLabelMarker"),
      e.consume(c),
      e.exit("gfmFootnoteCallLabelMarker"),
      s
    );
  }
  function s(c) {
    return c !== 94
      ? n(c)
      : (e.enter("gfmFootnoteCallMarker"),
        e.consume(c),
        e.exit("gfmFootnoteCallMarker"),
        e.enter("gfmFootnoteCallString"),
        (e.enter("chunkString").contentType = "string"),
        u);
  }
  function u(c) {
    if (o > 999 || (c === 93 && !l) || c === null || c === 91 || de(c))
      return n(c);
    if (c === 93) {
      e.exit("chunkString");
      const f = e.exit("gfmFootnoteCallString");
      return i.includes(Ct(r.sliceSerialize(f)))
        ? (e.enter("gfmFootnoteCallLabelMarker"),
          e.consume(c),
          e.exit("gfmFootnoteCallLabelMarker"),
          e.exit("gfmFootnoteCall"),
          t)
        : n(c);
    }
    return (de(c) || (l = !0), o++, e.consume(c), c === 92 ? d : u);
  }
  function d(c) {
    return c === 91 || c === 92 || c === 93 ? (e.consume(c), o++, u) : u(c);
  }
}
function bN(e, t, n) {
  const r = this,
    i = r.parser.gfmFootnotes || (r.parser.gfmFootnotes = []);
  let o,
    l = 0,
    a;
  return s;
  function s(g) {
    return (
      (e.enter("gfmFootnoteDefinition")._container = !0),
      e.enter("gfmFootnoteDefinitionLabel"),
      e.enter("gfmFootnoteDefinitionLabelMarker"),
      e.consume(g),
      e.exit("gfmFootnoteDefinitionLabelMarker"),
      u
    );
  }
  function u(g) {
    return g === 94
      ? (e.enter("gfmFootnoteDefinitionMarker"),
        e.consume(g),
        e.exit("gfmFootnoteDefinitionMarker"),
        e.enter("gfmFootnoteDefinitionLabelString"),
        (e.enter("chunkString").contentType = "string"),
        d)
      : n(g);
  }
  function d(g) {
    if (l > 999 || (g === 93 && !a) || g === null || g === 91 || de(g))
      return n(g);
    if (g === 93) {
      e.exit("chunkString");
      const y = e.exit("gfmFootnoteDefinitionLabelString");
      return (
        (o = Ct(r.sliceSerialize(y))),
        e.enter("gfmFootnoteDefinitionLabelMarker"),
        e.consume(g),
        e.exit("gfmFootnoteDefinitionLabelMarker"),
        e.exit("gfmFootnoteDefinitionLabel"),
        f
      );
    }
    return (de(g) || (a = !0), l++, e.consume(g), g === 92 ? c : d);
  }
  function c(g) {
    return g === 91 || g === 92 || g === 93 ? (e.consume(g), l++, d) : d(g);
  }
  function f(g) {
    return g === 58
      ? (e.enter("definitionMarker"),
        e.consume(g),
        e.exit("definitionMarker"),
        i.includes(o) || i.push(o),
        re(e, p, "gfmFootnoteDefinitionWhitespace"))
      : n(g);
  }
  function p(g) {
    return t(g);
  }
}
function vN(e, t, n) {
  return e.check(oo, t, e.attempt(pN, t, n));
}
function EN(e) {
  e.exit("gfmFootnoteDefinition");
}
function wN(e, t, n) {
  const r = this;
  return re(e, i, "gfmFootnoteDefinitionIndent", 5);
  function i(o) {
    const l = r.events[r.events.length - 1];
    return l &&
      l[1].type === "gfmFootnoteDefinitionIndent" &&
      l[2].sliceSerialize(l[1], !0).length === 4
      ? t(o)
      : n(o);
  }
}
function xN(e) {
  let n = (e || {}).singleTilde;
  const r = { name: "strikethrough", tokenize: o, resolveAll: i };
  return (
    n == null && (n = !0),
    {
      text: { 126: r },
      insideSpan: { null: [r] },
      attentionMarkers: { null: [126] },
    }
  );
  function i(l, a) {
    let s = -1;
    for (; ++s < l.length;)
      if (
        l[s][0] === "enter" &&
        l[s][1].type === "strikethroughSequenceTemporary" &&
        l[s][1]._close
      ) {
        let u = s;
        for (; u--;)
          if (
            l[u][0] === "exit" &&
            l[u][1].type === "strikethroughSequenceTemporary" &&
            l[u][1]._open &&
            l[s][1].end.offset - l[s][1].start.offset ===
              l[u][1].end.offset - l[u][1].start.offset
          ) {
            ((l[s][1].type = "strikethroughSequence"),
              (l[u][1].type = "strikethroughSequence"));
            const d = {
                type: "strikethrough",
                start: Object.assign({}, l[u][1].start),
                end: Object.assign({}, l[s][1].end),
              },
              c = {
                type: "strikethroughText",
                start: Object.assign({}, l[u][1].end),
                end: Object.assign({}, l[s][1].start),
              },
              f = [
                ["enter", d, a],
                ["enter", l[u][1], a],
                ["exit", l[u][1], a],
                ["enter", c, a],
              ],
              p = a.parser.constructs.insideSpan.null;
            (p && st(f, f.length, 0, Ql(p, l.slice(u + 1, s), a)),
              st(f, f.length, 0, [
                ["exit", c, a],
                ["enter", l[s][1], a],
                ["exit", l[s][1], a],
                ["exit", d, a],
              ]),
              st(l, u - 1, s - u + 3, f),
              (s = u + f.length - 2));
            break;
          }
      }
    for (s = -1; ++s < l.length;)
      l[s][1].type === "strikethroughSequenceTemporary" &&
        (l[s][1].type = "data");
    return l;
  }
  function o(l, a, s) {
    const u = this.previous,
      d = this.events;
    let c = 0;
    return f;
    function f(g) {
      return u === 126 && d[d.length - 1][1].type !== "characterEscape"
        ? s(g)
        : (l.enter("strikethroughSequenceTemporary"), p(g));
    }
    function p(g) {
      const y = Br(u);
      if (g === 126) return c > 1 ? s(g) : (l.consume(g), c++, p);
      if (c < 2 && !n) return s(g);
      const E = l.exit("strikethroughSequenceTemporary"),
        h = Br(g);
      return (
        (E._open = !h || (h === 2 && !!y)),
        (E._close = !y || (y === 2 && !!h)),
        a(g)
      );
    }
  }
}
class _N {
  constructor() {
    this.map = [];
  }
  add(t, n, r) {
    kN(this, t, n, r);
  }
  consume(t) {
    if (
      (this.map.sort(function (o, l) {
        return o[0] - l[0];
      }),
      this.map.length === 0)
    )
      return;
    let n = this.map.length;
    const r = [];
    for (; n > 0;)
      ((n -= 1),
        r.push(t.slice(this.map[n][0] + this.map[n][1]), this.map[n][2]),
        (t.length = this.map[n][0]));
    (r.push(t.slice()), (t.length = 0));
    let i = r.pop();
    for (; i;) {
      for (const o of i) t.push(o);
      i = r.pop();
    }
    this.map.length = 0;
  }
}
function kN(e, t, n, r) {
  let i = 0;
  if (!(n === 0 && r.length === 0)) {
    for (; i < e.map.length;) {
      if (e.map[i][0] === t) {
        ((e.map[i][1] += n), e.map[i][2].push(...r));
        return;
      }
      i += 1;
    }
    e.map.push([t, n, r]);
  }
}
function SN(e, t) {
  let n = !1;
  const r = [];
  for (; t < e.length;) {
    const i = e[t];
    if (n) {
      if (i[0] === "enter")
        i[1].type === "tableContent" &&
          r.push(e[t + 1][1].type === "tableDelimiterMarker" ? "left" : "none");
      else if (i[1].type === "tableContent") {
        if (e[t - 1][1].type === "tableDelimiterMarker") {
          const o = r.length - 1;
          r[o] = r[o] === "left" ? "center" : "right";
        }
      } else if (i[1].type === "tableDelimiterRow") break;
    } else i[0] === "enter" && i[1].type === "tableDelimiterRow" && (n = !0);
    t += 1;
  }
  return r;
}
function NN() {
  return { flow: { null: { name: "table", tokenize: CN, resolveAll: TN } } };
}
function CN(e, t, n) {
  const r = this;
  let i = 0,
    o = 0,
    l;
  return a;
  function a(S) {
    let F = r.events.length - 1;
    for (; F > -1;) {
      const V = r.events[F][1].type;
      if (V === "lineEnding" || V === "linePrefix") F--;
      else break;
    }
    const L = F > -1 ? r.events[F][1].type : null,
      Q = L === "tableHead" || L === "tableRow" ? x : s;
    return Q === x && r.parser.lazy[r.now().line] ? n(S) : Q(S);
  }
  function s(S) {
    return (e.enter("tableHead"), e.enter("tableRow"), u(S));
  }
  function u(S) {
    return (S === 124 || ((l = !0), (o += 1)), d(S));
  }
  function d(S) {
    return S === null
      ? n(S)
      : q(S)
        ? o > 1
          ? ((o = 0),
            (r.interrupt = !0),
            e.exit("tableRow"),
            e.enter("lineEnding"),
            e.consume(S),
            e.exit("lineEnding"),
            p)
          : n(S)
        : ee(S)
          ? re(e, d, "whitespace")(S)
          : ((o += 1),
            l && ((l = !1), (i += 1)),
            S === 124
              ? (e.enter("tableCellDivider"),
                e.consume(S),
                e.exit("tableCellDivider"),
                (l = !0),
                d)
              : (e.enter("data"), c(S)));
  }
  function c(S) {
    return S === null || S === 124 || de(S)
      ? (e.exit("data"), d(S))
      : (e.consume(S), S === 92 ? f : c);
  }
  function f(S) {
    return S === 92 || S === 124 ? (e.consume(S), c) : c(S);
  }
  function p(S) {
    return (
      (r.interrupt = !1),
      r.parser.lazy[r.now().line]
        ? n(S)
        : (e.enter("tableDelimiterRow"),
          (l = !1),
          ee(S)
            ? re(
                e,
                g,
                "linePrefix",
                r.parser.constructs.disable.null.includes("codeIndented")
                  ? void 0
                  : 4,
              )(S)
            : g(S))
    );
  }
  function g(S) {
    return S === 45 || S === 58
      ? E(S)
      : S === 124
        ? ((l = !0),
          e.enter("tableCellDivider"),
          e.consume(S),
          e.exit("tableCellDivider"),
          y)
        : N(S);
  }
  function y(S) {
    return ee(S) ? re(e, E, "whitespace")(S) : E(S);
  }
  function E(S) {
    return S === 58
      ? ((o += 1),
        (l = !0),
        e.enter("tableDelimiterMarker"),
        e.consume(S),
        e.exit("tableDelimiterMarker"),
        h)
      : S === 45
        ? ((o += 1), h(S))
        : S === null || q(S)
          ? _(S)
          : N(S);
  }
  function h(S) {
    return S === 45 ? (e.enter("tableDelimiterFiller"), m(S)) : N(S);
  }
  function m(S) {
    return S === 45
      ? (e.consume(S), m)
      : S === 58
        ? ((l = !0),
          e.exit("tableDelimiterFiller"),
          e.enter("tableDelimiterMarker"),
          e.consume(S),
          e.exit("tableDelimiterMarker"),
          b)
        : (e.exit("tableDelimiterFiller"), b(S));
  }
  function b(S) {
    return ee(S) ? re(e, _, "whitespace")(S) : _(S);
  }
  function _(S) {
    return S === 124
      ? g(S)
      : S === null || q(S)
        ? !l || i !== o
          ? N(S)
          : (e.exit("tableDelimiterRow"), e.exit("tableHead"), t(S))
        : N(S);
  }
  function N(S) {
    return n(S);
  }
  function x(S) {
    return (e.enter("tableRow"), O(S));
  }
  function O(S) {
    return S === 124
      ? (e.enter("tableCellDivider"),
        e.consume(S),
        e.exit("tableCellDivider"),
        O)
      : S === null || q(S)
        ? (e.exit("tableRow"), t(S))
        : ee(S)
          ? re(e, O, "whitespace")(S)
          : (e.enter("data"), I(S));
  }
  function I(S) {
    return S === null || S === 124 || de(S)
      ? (e.exit("data"), O(S))
      : (e.consume(S), S === 92 ? U : I);
  }
  function U(S) {
    return S === 92 || S === 124 ? (e.consume(S), I) : I(S);
  }
}
function TN(e, t) {
  let n = -1,
    r = !0,
    i = 0,
    o = [0, 0, 0, 0],
    l = [0, 0, 0, 0],
    a = !1,
    s = 0,
    u,
    d,
    c;
  const f = new _N();
  for (; ++n < e.length;) {
    const p = e[n],
      g = p[1];
    p[0] === "enter"
      ? g.type === "tableHead"
        ? ((a = !1),
          s !== 0 && (Wf(f, t, s, u, d), (d = void 0), (s = 0)),
          (u = {
            type: "table",
            start: Object.assign({}, g.start),
            end: Object.assign({}, g.end),
          }),
          f.add(n, 0, [["enter", u, t]]))
        : g.type === "tableRow" || g.type === "tableDelimiterRow"
          ? ((r = !0),
            (c = void 0),
            (o = [0, 0, 0, 0]),
            (l = [0, n + 1, 0, 0]),
            a &&
              ((a = !1),
              (d = {
                type: "tableBody",
                start: Object.assign({}, g.start),
                end: Object.assign({}, g.end),
              }),
              f.add(n, 0, [["enter", d, t]])),
            (i = g.type === "tableDelimiterRow" ? 2 : d ? 3 : 1))
          : i &&
              (g.type === "data" ||
                g.type === "tableDelimiterMarker" ||
                g.type === "tableDelimiterFiller")
            ? ((r = !1),
              l[2] === 0 &&
                (o[1] !== 0 &&
                  ((l[0] = l[1]),
                  (c = Ao(f, t, o, i, void 0, c)),
                  (o = [0, 0, 0, 0])),
                (l[2] = n)))
            : g.type === "tableCellDivider" &&
              (r
                ? (r = !1)
                : (o[1] !== 0 &&
                    ((l[0] = l[1]), (c = Ao(f, t, o, i, void 0, c))),
                  (o = l),
                  (l = [o[1], n, 0, 0])))
      : g.type === "tableHead"
        ? ((a = !0), (s = n))
        : g.type === "tableRow" || g.type === "tableDelimiterRow"
          ? ((s = n),
            o[1] !== 0
              ? ((l[0] = l[1]), (c = Ao(f, t, o, i, n, c)))
              : l[1] !== 0 && (c = Ao(f, t, l, i, n, c)),
            (i = 0))
          : i &&
            (g.type === "data" ||
              g.type === "tableDelimiterMarker" ||
              g.type === "tableDelimiterFiller") &&
            (l[3] = n);
  }
  for (
    s !== 0 && Wf(f, t, s, u, d), f.consume(t.events), n = -1;
    ++n < t.events.length;
  ) {
    const p = t.events[n];
    p[0] === "enter" &&
      p[1].type === "table" &&
      (p[1]._align = SN(t.events, n));
  }
  return e;
}
function Ao(e, t, n, r, i, o) {
  const l = r === 1 ? "tableHeader" : r === 2 ? "tableDelimiter" : "tableData",
    a = "tableContent";
  n[0] !== 0 &&
    ((o.end = Object.assign({}, ur(t.events, n[0]))),
    e.add(n[0], 0, [["exit", o, t]]));
  const s = ur(t.events, n[1]);
  if (
    ((o = { type: l, start: Object.assign({}, s), end: Object.assign({}, s) }),
    e.add(n[1], 0, [["enter", o, t]]),
    n[2] !== 0)
  ) {
    const u = ur(t.events, n[2]),
      d = ur(t.events, n[3]),
      c = { type: a, start: Object.assign({}, u), end: Object.assign({}, d) };
    if ((e.add(n[2], 0, [["enter", c, t]]), r !== 2)) {
      const f = t.events[n[2]],
        p = t.events[n[3]];
      if (
        ((f[1].end = Object.assign({}, p[1].end)),
        (f[1].type = "chunkText"),
        (f[1].contentType = "text"),
        n[3] > n[2] + 1)
      ) {
        const g = n[2] + 1,
          y = n[3] - n[2] - 1;
        e.add(g, y, []);
      }
    }
    e.add(n[3] + 1, 0, [["exit", c, t]]);
  }
  return (
    i !== void 0 &&
      ((o.end = Object.assign({}, ur(t.events, i))),
      e.add(i, 0, [["exit", o, t]]),
      (o = void 0)),
    o
  );
}
function Wf(e, t, n, r, i) {
  const o = [],
    l = ur(t.events, n);
  (i && ((i.end = Object.assign({}, l)), o.push(["exit", i, t])),
    (r.end = Object.assign({}, l)),
    o.push(["exit", r, t]),
    e.add(n + 1, 0, o));
}
function ur(e, t) {
  const n = e[t],
    r = n[0] === "enter" ? "start" : "end";
  return n[1][r];
}
const AN = { name: "tasklistCheck", tokenize: ON };
function RN() {
  return { text: { 91: AN } };
}
function ON(e, t, n) {
  const r = this;
  return i;
  function i(s) {
    return r.previous !== null || !r._gfmTasklistFirstContentOfListItem
      ? n(s)
      : (e.enter("taskListCheck"),
        e.enter("taskListCheckMarker"),
        e.consume(s),
        e.exit("taskListCheckMarker"),
        o);
  }
  function o(s) {
    return de(s)
      ? (e.enter("taskListCheckValueUnchecked"),
        e.consume(s),
        e.exit("taskListCheckValueUnchecked"),
        l)
      : s === 88 || s === 120
        ? (e.enter("taskListCheckValueChecked"),
          e.consume(s),
          e.exit("taskListCheckValueChecked"),
          l)
        : n(s);
  }
  function l(s) {
    return s === 93
      ? (e.enter("taskListCheckMarker"),
        e.consume(s),
        e.exit("taskListCheckMarker"),
        e.exit("taskListCheck"),
        a)
      : n(s);
  }
  function a(s) {
    return q(s) ? t(s) : ee(s) ? e.check({ tokenize: IN }, t, n)(s) : n(s);
  }
}
function IN(e, t, n) {
  return re(e, r, "whitespace");
  function r(i) {
    return i === null ? n(i) : t(i);
  }
}
function MN(e) {
  return im([iN(), hN(), xN(e), NN(), RN()]);
}
const LN = {};
function DN(e) {
  const t = this,
    n = e || LN,
    r = t.data(),
    i = r.micromarkExtensions || (r.micromarkExtensions = []),
    o = r.fromMarkdownExtensions || (r.fromMarkdownExtensions = []),
    l = r.toMarkdownExtensions || (r.toMarkdownExtensions = []);
  (i.push(MN(n)), o.push(eN()), l.push(tN(n)));
}
const Gf = function (e, t, n) {
    const r = lo(n);
    if (!e || !e.type || !e.children) throw new Error("Expected parent node");
    if (typeof t == "number") {
      if (t < 0 || t === Number.POSITIVE_INFINITY)
        throw new Error("Expected positive finite number as index");
    } else if (((t = e.children.indexOf(t)), t < 0))
      throw new Error("Expected child node or index");
    for (; ++t < e.children.length;)
      if (r(e.children[t], t, e)) return e.children[t];
  },
  nr = function (e) {
    if (e == null) return FN;
    if (typeof e == "string") return zN(e);
    if (typeof e == "object") return PN(e);
    if (typeof e == "function") return xc(e);
    throw new Error("Expected function, string, or array as `test`");
  };
function PN(e) {
  const t = [];
  let n = -1;
  for (; ++n < e.length;) t[n] = nr(e[n]);
  return xc(r);
  function r(...i) {
    let o = -1;
    for (; ++o < t.length;) if (t[o].apply(this, i)) return !0;
    return !1;
  }
}
function zN(e) {
  return xc(t);
  function t(n) {
    return n.tagName === e;
  }
}
function xc(e) {
  return t;
  function t(n, r, i) {
    return !!(
      BN(n) && e.call(this, n, typeof r == "number" ? r : void 0, i || void 0)
    );
  }
}
function FN(e) {
  return !!(
    e &&
    typeof e == "object" &&
    "type" in e &&
    e.type === "element" &&
    "tagName" in e &&
    typeof e.tagName == "string"
  );
}
function BN(e) {
  return e !== null && typeof e == "object" && "type" in e && "tagName" in e;
}
const Kf = /\n/g,
  Vf = /[\t ]+/g,
  ru = nr("br"),
  qf = nr(VN),
  UN = nr("p"),
  Yf = nr("tr"),
  $N = nr([
    "datalist",
    "head",
    "noembed",
    "noframes",
    "noscript",
    "rp",
    "script",
    "style",
    "template",
    "title",
    KN,
    qN,
  ]),
  Qm = nr([
    "address",
    "article",
    "aside",
    "blockquote",
    "body",
    "caption",
    "center",
    "dd",
    "dialog",
    "dir",
    "dl",
    "dt",
    "div",
    "figure",
    "figcaption",
    "footer",
    "form,",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "header",
    "hgroup",
    "hr",
    "html",
    "legend",
    "li",
    "listing",
    "main",
    "menu",
    "nav",
    "ol",
    "p",
    "plaintext",
    "pre",
    "section",
    "ul",
    "xmp",
  ]);
function HN(e, t) {
  const n = t || {},
    r = "children" in e ? e.children : [],
    i = Qm(e),
    o = Jm(e, { whitespace: n.whitespace || "normal" }),
    l = [];
  (e.type === "text" || e.type === "comment") &&
    l.push(...Xm(e, { breakBefore: !0, breakAfter: !0 }));
  let a = -1;
  for (; ++a < r.length;)
    l.push(
      ...Zm(r[a], e, {
        whitespace: o,
        breakBefore: a ? void 0 : i,
        breakAfter: a < r.length - 1 ? ru(r[a + 1]) : i,
      }),
    );
  const s = [];
  let u;
  for (a = -1; ++a < l.length;) {
    const d = l[a];
    typeof d == "number"
      ? u !== void 0 && d > u && (u = d)
      : d &&
        (u !== void 0 &&
          u > -1 &&
          s.push(
            `
`.repeat(u) || " ",
          ),
        (u = -1),
        s.push(d));
  }
  return s.join("");
}
function Zm(e, t, n) {
  return e.type === "element"
    ? jN(e, t, n)
    : e.type === "text"
      ? n.whitespace === "normal"
        ? Xm(e, n)
        : WN(e)
      : [];
}
function jN(e, t, n) {
  const r = Jm(e, n),
    i = e.children || [];
  let o = -1,
    l = [];
  if ($N(e)) return l;
  let a, s;
  for (
    ru(e) || (Yf(e) && Gf(t, e, Yf))
      ? (s = `
`)
      : UN(e)
        ? ((a = 2), (s = 2))
        : Qm(e) && ((a = 1), (s = 1));
    ++o < i.length;
  )
    l = l.concat(
      Zm(i[o], e, {
        whitespace: r,
        breakBefore: o ? void 0 : a,
        breakAfter: o < i.length - 1 ? ru(i[o + 1]) : s,
      }),
    );
  return (
    qf(e) && Gf(t, e, qf) && l.push("	"),
    a && l.unshift(a),
    s && l.push(s),
    l
  );
}
function Xm(e, t) {
  const n = String(e.value),
    r = [],
    i = [];
  let o = 0;
  for (; o <= n.length;) {
    Kf.lastIndex = o;
    const s = Kf.exec(n),
      u = s && "index" in s ? s.index : n.length;
    (r.push(
      GN(
        n
          .slice(o, u)
          .replace(/[\u061C\u200E\u200F\u202A-\u202E\u2066-\u2069]/g, ""),
        o === 0 ? t.breakBefore : !0,
        u === n.length ? t.breakAfter : !0,
      ),
    ),
      (o = u + 1));
  }
  let l = -1,
    a;
  for (; ++l < r.length;)
    r[l].charCodeAt(r[l].length - 1) === 8203 ||
    (l < r.length - 1 && r[l + 1].charCodeAt(0) === 8203)
      ? (i.push(r[l]), (a = void 0))
      : r[l]
        ? (typeof a == "number" && i.push(a), i.push(r[l]), (a = 0))
        : (l === 0 || l === r.length - 1) && i.push(0);
  return i;
}
function WN(e) {
  return [String(e.value)];
}
function GN(e, t, n) {
  const r = [];
  let i = 0,
    o;
  for (; i < e.length;) {
    Vf.lastIndex = i;
    const l = Vf.exec(e);
    ((o = l ? l.index : e.length),
      !i && !o && l && !t && r.push(""),
      i !== o && r.push(e.slice(i, o)),
      (i = l ? o + l[0].length : o));
  }
  return (i !== o && !n && r.push(""), r.join(" "));
}
function Jm(e, t) {
  if (e.type === "element") {
    const n = e.properties || {};
    switch (e.tagName) {
      case "listing":
      case "plaintext":
      case "xmp":
        return "pre";
      case "nobr":
        return "nowrap";
      case "pre":
        return n.wrap ? "pre-wrap" : "pre";
      case "td":
      case "th":
        return n.noWrap ? "nowrap" : t.whitespace;
      case "textarea":
        return "pre-wrap";
    }
  }
  return t.whitespace;
}
function KN(e) {
  return !!(e.properties || {}).hidden;
}
function VN(e) {
  return e.tagName === "td" || e.tagName === "th";
}
function qN(e) {
  return e.tagName === "dialog" && !(e.properties || {}).open;
}
function YN(e) {
  const t = e.regex,
    n = e.COMMENT("//", "$", { contains: [{ begin: /\\\n/ }] }),
    r = "decltype\\(auto\\)",
    i = "[a-zA-Z_]\\w*::",
    l =
      "(?!struct)(" +
      r +
      "|" +
      t.optional(i) +
      "[a-zA-Z_]\\w*" +
      t.optional("<[^<>]+>") +
      ")",
    a = { className: "type", begin: "\\b[a-z\\d_]*_t\\b" },
    u = {
      className: "string",
      variants: [
        {
          begin: '(u8?|U|L)?"',
          end: '"',
          illegal: "\\n",
          contains: [e.BACKSLASH_ESCAPE],
        },
        {
          begin:
            "(u8?|U|L)?'(" +
            "\\\\(x[0-9A-Fa-f]{2}|u[0-9A-Fa-f]{4,8}|[0-7]{3}|\\S)" +
            "|.)",
          end: "'",
          illegal: ".",
        },
        e.END_SAME_AS_BEGIN({
          begin: /(?:u8?|U|L)?R"([^()\\ ]{0,16})\(/,
          end: /\)([^()\\ ]{0,16})"/,
        }),
      ],
    },
    d = {
      className: "number",
      variants: [
        {
          begin:
            "[+-]?(?:(?:[0-9](?:'?[0-9])*\\.(?:[0-9](?:'?[0-9])*)?|\\.[0-9](?:'?[0-9])*)(?:[Ee][+-]?[0-9](?:'?[0-9])*)?|[0-9](?:'?[0-9])*[Ee][+-]?[0-9](?:'?[0-9])*|0[Xx](?:[0-9A-Fa-f](?:'?[0-9A-Fa-f])*(?:\\.(?:[0-9A-Fa-f](?:'?[0-9A-Fa-f])*)?)?|\\.[0-9A-Fa-f](?:'?[0-9A-Fa-f])*)[Pp][+-]?[0-9](?:'?[0-9])*)(?:[Ff](?:16|32|64|128)?|(BF|bf)16|[Ll]|)",
        },
        {
          begin:
            "[+-]?\\b(?:0[Bb][01](?:'?[01])*|0[Xx][0-9A-Fa-f](?:'?[0-9A-Fa-f])*|0(?:'?[0-7])*|[1-9](?:'?[0-9])*)(?:[Uu](?:LL?|ll?)|[Uu][Zz]?|(?:LL?|ll?)[Uu]?|[Zz][Uu]|)",
        },
      ],
      relevance: 0,
    },
    c = {
      className: "meta",
      begin: /#\s*[a-z]+\b/,
      end: /$/,
      keywords: {
        keyword:
          "if else elif endif define undef warning error line pragma _Pragma ifdef ifndef include",
      },
      contains: [
        { begin: /\\\n/, relevance: 0 },
        e.inherit(u, { className: "string" }),
        { className: "string", begin: /<.*?>/ },
        n,
        e.C_BLOCK_COMMENT_MODE,
      ],
    },
    f = { className: "title", begin: t.optional(i) + e.IDENT_RE, relevance: 0 },
    p = t.optional(i) + e.IDENT_RE + "\\s*\\(",
    g = [
      "alignas",
      "alignof",
      "and",
      "and_eq",
      "asm",
      "atomic_cancel",
      "atomic_commit",
      "atomic_noexcept",
      "auto",
      "bitand",
      "bitor",
      "break",
      "case",
      "catch",
      "class",
      "co_await",
      "co_return",
      "co_yield",
      "compl",
      "concept",
      "const_cast|10",
      "consteval",
      "constexpr",
      "constinit",
      "continue",
      "decltype",
      "default",
      "delete",
      "do",
      "dynamic_cast|10",
      "else",
      "enum",
      "explicit",
      "export",
      "extern",
      "false",
      "final",
      "for",
      "friend",
      "goto",
      "if",
      "import",
      "inline",
      "module",
      "mutable",
      "namespace",
      "new",
      "noexcept",
      "not",
      "not_eq",
      "nullptr",
      "operator",
      "or",
      "or_eq",
      "override",
      "private",
      "protected",
      "public",
      "reflexpr",
      "register",
      "reinterpret_cast|10",
      "requires",
      "return",
      "sizeof",
      "static_assert",
      "static_cast|10",
      "struct",
      "switch",
      "synchronized",
      "template",
      "this",
      "thread_local",
      "throw",
      "transaction_safe",
      "transaction_safe_dynamic",
      "true",
      "try",
      "typedef",
      "typeid",
      "typename",
      "union",
      "using",
      "virtual",
      "volatile",
      "while",
      "xor",
      "xor_eq",
    ],
    y = [
      "bool",
      "char",
      "char16_t",
      "char32_t",
      "char8_t",
      "double",
      "float",
      "int",
      "long",
      "short",
      "void",
      "wchar_t",
      "unsigned",
      "signed",
      "const",
      "static",
    ],
    E = [
      "any",
      "auto_ptr",
      "barrier",
      "binary_semaphore",
      "bitset",
      "complex",
      "condition_variable",
      "condition_variable_any",
      "counting_semaphore",
      "deque",
      "false_type",
      "flat_map",
      "flat_set",
      "future",
      "imaginary",
      "initializer_list",
      "istringstream",
      "jthread",
      "latch",
      "lock_guard",
      "multimap",
      "multiset",
      "mutex",
      "optional",
      "ostringstream",
      "packaged_task",
      "pair",
      "promise",
      "priority_queue",
      "queue",
      "recursive_mutex",
      "recursive_timed_mutex",
      "scoped_lock",
      "set",
      "shared_future",
      "shared_lock",
      "shared_mutex",
      "shared_timed_mutex",
      "shared_ptr",
      "stack",
      "string_view",
      "stringstream",
      "timed_mutex",
      "thread",
      "true_type",
      "tuple",
      "unique_lock",
      "unique_ptr",
      "unordered_map",
      "unordered_multimap",
      "unordered_multiset",
      "unordered_set",
      "variant",
      "vector",
      "weak_ptr",
      "wstring",
      "wstring_view",
    ],
    h = [
      "abort",
      "abs",
      "acos",
      "apply",
      "as_const",
      "asin",
      "atan",
      "atan2",
      "calloc",
      "ceil",
      "cerr",
      "cin",
      "clog",
      "cos",
      "cosh",
      "cout",
      "declval",
      "endl",
      "exchange",
      "exit",
      "exp",
      "fabs",
      "floor",
      "fmod",
      "forward",
      "fprintf",
      "fputs",
      "free",
      "frexp",
      "fscanf",
      "future",
      "invoke",
      "isalnum",
      "isalpha",
      "iscntrl",
      "isdigit",
      "isgraph",
      "islower",
      "isprint",
      "ispunct",
      "isspace",
      "isupper",
      "isxdigit",
      "labs",
      "launder",
      "ldexp",
      "log",
      "log10",
      "make_pair",
      "make_shared",
      "make_shared_for_overwrite",
      "make_tuple",
      "make_unique",
      "malloc",
      "memchr",
      "memcmp",
      "memcpy",
      "memset",
      "modf",
      "move",
      "pow",
      "printf",
      "putchar",
      "puts",
      "realloc",
      "scanf",
      "sin",
      "sinh",
      "snprintf",
      "sprintf",
      "sqrt",
      "sscanf",
      "std",
      "stderr",
      "stdin",
      "stdout",
      "strcat",
      "strchr",
      "strcmp",
      "strcpy",
      "strcspn",
      "strlen",
      "strncat",
      "strncmp",
      "strncpy",
      "strpbrk",
      "strrchr",
      "strspn",
      "strstr",
      "swap",
      "tan",
      "tanh",
      "terminate",
      "to_underlying",
      "tolower",
      "toupper",
      "vfprintf",
      "visit",
      "vprintf",
      "vsprintf",
    ],
    _ = {
      type: y,
      keyword: g,
      literal: ["NULL", "false", "nullopt", "nullptr", "true"],
      built_in: ["_Pragma"],
      _type_hints: E,
    },
    N = {
      className: "function.dispatch",
      relevance: 0,
      keywords: { _hint: h },
      begin: t.concat(
        /\b/,
        /(?!decltype)/,
        /(?!if)/,
        /(?!for)/,
        /(?!switch)/,
        /(?!while)/,
        e.IDENT_RE,
        t.lookahead(/(<[^<>]+>|)\s*\(/),
      ),
    },
    x = [N, c, a, n, e.C_BLOCK_COMMENT_MODE, d, u],
    O = {
      variants: [
        { begin: /=/, end: /;/ },
        { begin: /\(/, end: /\)/ },
        { beginKeywords: "new throw return else", end: /;/ },
      ],
      keywords: _,
      contains: x.concat([
        {
          begin: /\(/,
          end: /\)/,
          keywords: _,
          contains: x.concat(["self"]),
          relevance: 0,
        },
      ]),
      relevance: 0,
    },
    I = {
      className: "function",
      begin: "(" + l + "[\\*&\\s]+)+" + p,
      returnBegin: !0,
      end: /[{;=]/,
      excludeEnd: !0,
      keywords: _,
      illegal: /[^\w\s\*&:<>.]/,
      contains: [
        { begin: r, keywords: _, relevance: 0 },
        { begin: p, returnBegin: !0, contains: [f], relevance: 0 },
        { begin: /::/, relevance: 0 },
        { begin: /:/, endsWithParent: !0, contains: [u, d] },
        { relevance: 0, match: /,/ },
        {
          className: "params",
          begin: /\(/,
          end: /\)/,
          keywords: _,
          relevance: 0,
          contains: [
            n,
            e.C_BLOCK_COMMENT_MODE,
            u,
            d,
            a,
            {
              begin: /\(/,
              end: /\)/,
              keywords: _,
              relevance: 0,
              contains: ["self", n, e.C_BLOCK_COMMENT_MODE, u, d, a],
            },
          ],
        },
        a,
        n,
        e.C_BLOCK_COMMENT_MODE,
        c,
      ],
    };
  return {
    name: "C++",
    aliases: ["cc", "c++", "h++", "hpp", "hh", "hxx", "cxx"],
    keywords: _,
    illegal: "</",
    classNameAliases: { "function.dispatch": "built_in" },
    contains: [].concat(O, I, N, x, [
      c,
      {
        begin:
          "\\b(deque|list|queue|priority_queue|pair|stack|vector|map|set|bitset|multiset|multimap|unordered_map|unordered_set|unordered_multiset|unordered_multimap|array|tuple|optional|variant|function|flat_map|flat_set)\\s*<(?!<)",
        end: ">",
        keywords: _,
        contains: ["self", a],
      },
      { begin: e.IDENT_RE + "::", keywords: _ },
      {
        match: [
          /\b(?:enum(?:\s+(?:class|struct))?|class|struct|union)/,
          /\s+/,
          /\w+/,
        ],
        className: { 1: "keyword", 3: "title.class" },
      },
    ]),
  };
}
function QN(e) {
  const t = {
      type: ["boolean", "byte", "word", "String"],
      built_in: [
        "KeyboardController",
        "MouseController",
        "SoftwareSerial",
        "EthernetServer",
        "EthernetClient",
        "LiquidCrystal",
        "RobotControl",
        "GSMVoiceCall",
        "EthernetUDP",
        "EsploraTFT",
        "HttpClient",
        "RobotMotor",
        "WiFiClient",
        "GSMScanner",
        "FileSystem",
        "Scheduler",
        "GSMServer",
        "YunClient",
        "YunServer",
        "IPAddress",
        "GSMClient",
        "GSMModem",
        "Keyboard",
        "Ethernet",
        "Console",
        "GSMBand",
        "Esplora",
        "Stepper",
        "Process",
        "WiFiUDP",
        "GSM_SMS",
        "Mailbox",
        "USBHost",
        "Firmata",
        "PImage",
        "Client",
        "Server",
        "GSMPIN",
        "FileIO",
        "Bridge",
        "Serial",
        "EEPROM",
        "Stream",
        "Mouse",
        "Audio",
        "Servo",
        "File",
        "Task",
        "GPRS",
        "WiFi",
        "Wire",
        "TFT",
        "GSM",
        "SPI",
        "SD",
      ],
      _hints: [
        "setup",
        "loop",
        "runShellCommandAsynchronously",
        "analogWriteResolution",
        "retrieveCallingNumber",
        "printFirmwareVersion",
        "analogReadResolution",
        "sendDigitalPortPair",
        "noListenOnLocalhost",
        "readJoystickButton",
        "setFirmwareVersion",
        "readJoystickSwitch",
        "scrollDisplayRight",
        "getVoiceCallStatus",
        "scrollDisplayLeft",
        "writeMicroseconds",
        "delayMicroseconds",
        "beginTransmission",
        "getSignalStrength",
        "runAsynchronously",
        "getAsynchronously",
        "listenOnLocalhost",
        "getCurrentCarrier",
        "readAccelerometer",
        "messageAvailable",
        "sendDigitalPorts",
        "lineFollowConfig",
        "countryNameWrite",
        "runShellCommand",
        "readStringUntil",
        "rewindDirectory",
        "readTemperature",
        "setClockDivider",
        "readLightSensor",
        "endTransmission",
        "analogReference",
        "detachInterrupt",
        "countryNameRead",
        "attachInterrupt",
        "encryptionType",
        "readBytesUntil",
        "robotNameWrite",
        "readMicrophone",
        "robotNameRead",
        "cityNameWrite",
        "userNameWrite",
        "readJoystickY",
        "readJoystickX",
        "mouseReleased",
        "openNextFile",
        "scanNetworks",
        "noInterrupts",
        "digitalWrite",
        "beginSpeaker",
        "mousePressed",
        "isActionDone",
        "mouseDragged",
        "displayLogos",
        "noAutoscroll",
        "addParameter",
        "remoteNumber",
        "getModifiers",
        "keyboardRead",
        "userNameRead",
        "waitContinue",
        "processInput",
        "parseCommand",
        "printVersion",
        "readNetworks",
        "writeMessage",
        "blinkVersion",
        "cityNameRead",
        "readMessage",
        "setDataMode",
        "parsePacket",
        "isListening",
        "setBitOrder",
        "beginPacket",
        "isDirectory",
        "motorsWrite",
        "drawCompass",
        "digitalRead",
        "clearScreen",
        "serialEvent",
        "rightToLeft",
        "setTextSize",
        "leftToRight",
        "requestFrom",
        "keyReleased",
        "compassRead",
        "analogWrite",
        "interrupts",
        "WiFiServer",
        "disconnect",
        "playMelody",
        "parseFloat",
        "autoscroll",
        "getPINUsed",
        "setPINUsed",
        "setTimeout",
        "sendAnalog",
        "readSlider",
        "analogRead",
        "beginWrite",
        "createChar",
        "motorsStop",
        "keyPressed",
        "tempoWrite",
        "readButton",
        "subnetMask",
        "debugPrint",
        "macAddress",
        "writeGreen",
        "randomSeed",
        "attachGPRS",
        "readString",
        "sendString",
        "remotePort",
        "releaseAll",
        "mouseMoved",
        "background",
        "getXChange",
        "getYChange",
        "answerCall",
        "getResult",
        "voiceCall",
        "endPacket",
        "constrain",
        "getSocket",
        "writeJSON",
        "getButton",
        "available",
        "connected",
        "findUntil",
        "readBytes",
        "exitValue",
        "readGreen",
        "writeBlue",
        "startLoop",
        "IPAddress",
        "isPressed",
        "sendSysex",
        "pauseMode",
        "gatewayIP",
        "setCursor",
        "getOemKey",
        "tuneWrite",
        "noDisplay",
        "loadImage",
        "switchPIN",
        "onRequest",
        "onReceive",
        "changePIN",
        "playFile",
        "noBuffer",
        "parseInt",
        "overflow",
        "checkPIN",
        "knobRead",
        "beginTFT",
        "bitClear",
        "updateIR",
        "bitWrite",
        "position",
        "writeRGB",
        "highByte",
        "writeRed",
        "setSpeed",
        "readBlue",
        "noStroke",
        "remoteIP",
        "transfer",
        "shutdown",
        "hangCall",
        "beginSMS",
        "endWrite",
        "attached",
        "maintain",
        "noCursor",
        "checkReg",
        "checkPUK",
        "shiftOut",
        "isValid",
        "shiftIn",
        "pulseIn",
        "connect",
        "println",
        "localIP",
        "pinMode",
        "getIMEI",
        "display",
        "noBlink",
        "process",
        "getBand",
        "running",
        "beginSD",
        "drawBMP",
        "lowByte",
        "setBand",
        "release",
        "bitRead",
        "prepare",
        "pointTo",
        "readRed",
        "setMode",
        "noFill",
        "remove",
        "listen",
        "stroke",
        "detach",
        "attach",
        "noTone",
        "exists",
        "buffer",
        "height",
        "bitSet",
        "circle",
        "config",
        "cursor",
        "random",
        "IRread",
        "setDNS",
        "endSMS",
        "getKey",
        "micros",
        "millis",
        "begin",
        "print",
        "write",
        "ready",
        "flush",
        "width",
        "isPIN",
        "blink",
        "clear",
        "press",
        "mkdir",
        "rmdir",
        "close",
        "point",
        "yield",
        "image",
        "BSSID",
        "click",
        "delay",
        "read",
        "text",
        "move",
        "peek",
        "beep",
        "rect",
        "line",
        "open",
        "seek",
        "fill",
        "size",
        "turn",
        "stop",
        "home",
        "find",
        "step",
        "tone",
        "sqrt",
        "RSSI",
        "SSID",
        "end",
        "bit",
        "tan",
        "cos",
        "sin",
        "pow",
        "map",
        "abs",
        "max",
        "min",
        "get",
        "run",
        "put",
      ],
      literal: [
        "DIGITAL_MESSAGE",
        "FIRMATA_STRING",
        "ANALOG_MESSAGE",
        "REPORT_DIGITAL",
        "REPORT_ANALOG",
        "INPUT_PULLUP",
        "SET_PIN_MODE",
        "INTERNAL2V56",
        "SYSTEM_RESET",
        "LED_BUILTIN",
        "INTERNAL1V1",
        "SYSEX_START",
        "INTERNAL",
        "EXTERNAL",
        "DEFAULT",
        "OUTPUT",
        "INPUT",
        "HIGH",
        "LOW",
      ],
    },
    n = YN(e),
    r = n.keywords;
  return (
    (r.type = [...r.type, ...t.type]),
    (r.literal = [...r.literal, ...t.literal]),
    (r.built_in = [...r.built_in, ...t.built_in]),
    (r._hints = t._hints),
    (n.name = "Arduino"),
    (n.aliases = ["ino"]),
    (n.supersetOf = "cpp"),
    n
  );
}
function ZN(e) {
  const t = e.regex,
    n = {},
    r = {
      begin: /\$\{/,
      end: /\}/,
      contains: ["self", { begin: /:-/, contains: [n] }],
    };
  Object.assign(n, {
    className: "variable",
    variants: [
      { begin: t.concat(/\$[\w\d#@][\w\d_]*/, "(?![\\w\\d])(?![$])") },
      r,
    ],
  });
  const i = {
      className: "subst",
      begin: /\$\(/,
      end: /\)/,
      contains: [e.BACKSLASH_ESCAPE],
    },
    o = e.inherit(e.COMMENT(), {
      match: [/(^|\s)/, /#.*$/],
      scope: { 2: "comment" },
    }),
    l = {
      begin: /<<-?\s*(?=\w+)/,
      starts: {
        contains: [
          e.END_SAME_AS_BEGIN({
            begin: /(\w+)/,
            end: /(\w+)/,
            className: "string",
          }),
        ],
      },
    },
    a = {
      className: "string",
      begin: /"/,
      end: /"/,
      contains: [e.BACKSLASH_ESCAPE, n, i],
    };
  i.contains.push(a);
  const s = { match: /\\"/ },
    u = { className: "string", begin: /'/, end: /'/ },
    d = { match: /\\'/ },
    c = {
      begin: /\$?\(\(/,
      end: /\)\)/,
      contains: [
        { begin: /\d+#[0-9a-f]+/, className: "number" },
        e.NUMBER_MODE,
        n,
      ],
    },
    f = ["fish", "bash", "zsh", "sh", "csh", "ksh", "tcsh", "dash", "scsh"],
    p = e.SHEBANG({ binary: `(${f.join("|")})`, relevance: 10 }),
    g = {
      className: "function",
      begin: /\w[\w\d_]*\s*\(\s*\)\s*\{/,
      returnBegin: !0,
      contains: [e.inherit(e.TITLE_MODE, { begin: /\w[\w\d_]*/ })],
      relevance: 0,
    },
    y = [
      "if",
      "then",
      "else",
      "elif",
      "fi",
      "time",
      "for",
      "while",
      "until",
      "in",
      "do",
      "done",
      "case",
      "esac",
      "coproc",
      "function",
      "select",
    ],
    E = ["true", "false"],
    h = { match: /(\/[a-z._-]+)+/ },
    m = [
      "break",
      "cd",
      "continue",
      "eval",
      "exec",
      "exit",
      "export",
      "getopts",
      "hash",
      "pwd",
      "readonly",
      "return",
      "shift",
      "test",
      "times",
      "trap",
      "umask",
      "unset",
    ],
    b = [
      "alias",
      "bind",
      "builtin",
      "caller",
      "command",
      "declare",
      "echo",
      "enable",
      "help",
      "let",
      "local",
      "logout",
      "mapfile",
      "printf",
      "read",
      "readarray",
      "source",
      "sudo",
      "type",
      "typeset",
      "ulimit",
      "unalias",
    ],
    _ = [
      "autoload",
      "bg",
      "bindkey",
      "bye",
      "cap",
      "chdir",
      "clone",
      "comparguments",
      "compcall",
      "compctl",
      "compdescribe",
      "compfiles",
      "compgroups",
      "compquote",
      "comptags",
      "comptry",
      "compvalues",
      "dirs",
      "disable",
      "disown",
      "echotc",
      "echoti",
      "emulate",
      "fc",
      "fg",
      "float",
      "functions",
      "getcap",
      "getln",
      "history",
      "integer",
      "jobs",
      "kill",
      "limit",
      "log",
      "noglob",
      "popd",
      "print",
      "pushd",
      "pushln",
      "rehash",
      "sched",
      "setcap",
      "setopt",
      "stat",
      "suspend",
      "ttyctl",
      "unfunction",
      "unhash",
      "unlimit",
      "unsetopt",
      "vared",
      "wait",
      "whence",
      "where",
      "which",
      "zcompile",
      "zformat",
      "zftp",
      "zle",
      "zmodload",
      "zparseopts",
      "zprof",
      "zpty",
      "zregexparse",
      "zsocket",
      "zstyle",
      "ztcp",
    ],
    N = [
      "chcon",
      "chgrp",
      "chown",
      "chmod",
      "cp",
      "dd",
      "df",
      "dir",
      "dircolors",
      "ln",
      "ls",
      "mkdir",
      "mkfifo",
      "mknod",
      "mktemp",
      "mv",
      "realpath",
      "rm",
      "rmdir",
      "shred",
      "sync",
      "touch",
      "truncate",
      "vdir",
      "b2sum",
      "base32",
      "base64",
      "cat",
      "cksum",
      "comm",
      "csplit",
      "cut",
      "expand",
      "fmt",
      "fold",
      "head",
      "join",
      "md5sum",
      "nl",
      "numfmt",
      "od",
      "paste",
      "ptx",
      "pr",
      "sha1sum",
      "sha224sum",
      "sha256sum",
      "sha384sum",
      "sha512sum",
      "shuf",
      "sort",
      "split",
      "sum",
      "tac",
      "tail",
      "tr",
      "tsort",
      "unexpand",
      "uniq",
      "wc",
      "arch",
      "basename",
      "chroot",
      "date",
      "dirname",
      "du",
      "echo",
      "env",
      "expr",
      "factor",
      "groups",
      "hostid",
      "id",
      "link",
      "logname",
      "nice",
      "nohup",
      "nproc",
      "pathchk",
      "pinky",
      "printenv",
      "printf",
      "pwd",
      "readlink",
      "runcon",
      "seq",
      "sleep",
      "stat",
      "stdbuf",
      "stty",
      "tee",
      "test",
      "timeout",
      "tty",
      "uname",
      "unlink",
      "uptime",
      "users",
      "who",
      "whoami",
      "yes",
    ];
  return {
    name: "Bash",
    aliases: ["sh", "zsh"],
    keywords: {
      $pattern: /\b[a-z][a-z0-9._-]+\b/,
      keyword: y,
      literal: E,
      built_in: [...m, ...b, "set", "shopt", ..._, ...N],
    },
    contains: [p, e.SHEBANG(), g, c, o, l, h, a, s, u, d, n],
  };
}
function XN(e) {
  const t = e.regex,
    n = e.COMMENT("//", "$", { contains: [{ begin: /\\\n/ }] }),
    r = "decltype\\(auto\\)",
    i = "[a-zA-Z_]\\w*::",
    l =
      "(" +
      r +
      "|" +
      t.optional(i) +
      "[a-zA-Z_]\\w*" +
      t.optional("<[^<>]+>") +
      ")",
    a = {
      className: "type",
      variants: [
        { begin: "\\b[a-z\\d_]*_t\\b" },
        { match: /\batomic_[a-z]{3,6}\b/ },
      ],
    },
    u = {
      className: "string",
      variants: [
        {
          begin: '(u8?|U|L)?"',
          end: '"',
          illegal: "\\n",
          contains: [e.BACKSLASH_ESCAPE],
        },
        {
          begin:
            "(u8?|U|L)?'(" +
            "\\\\(x[0-9A-Fa-f]{2}|u[0-9A-Fa-f]{4,8}|[0-7]{3}|\\S)" +
            "|.)",
          end: "'",
          illegal: ".",
        },
        e.END_SAME_AS_BEGIN({
          begin: /(?:u8?|U|L)?R"([^()\\ ]{0,16})\(/,
          end: /\)([^()\\ ]{0,16})"/,
        }),
      ],
    },
    d = {
      className: "number",
      variants: [
        { match: /\b(0b[01']+)/ },
        {
          match:
            /(-?)\b([\d']+(\.[\d']*)?|\.[\d']+)((ll|LL|l|L)(u|U)?|(u|U)(ll|LL|l|L)?|f|F|b|B)/,
        },
        {
          match:
            /(-?)\b(0[xX][a-fA-F0-9]+(?:'[a-fA-F0-9]+)*(?:\.[a-fA-F0-9]*(?:'[a-fA-F0-9]*)*)?(?:[pP][-+]?[0-9]+)?(l|L)?(u|U)?)/,
        },
        { match: /(-?)\b\d+(?:'\d+)*(?:\.\d*(?:'\d*)*)?(?:[eE][-+]?\d+)?/ },
      ],
      relevance: 0,
    },
    c = {
      className: "meta",
      begin: /#\s*[a-z]+\b/,
      end: /$/,
      keywords: {
        keyword:
          "if else elif endif define undef warning error line pragma _Pragma ifdef ifndef elifdef elifndef include",
      },
      contains: [
        { begin: /\\\n/, relevance: 0 },
        e.inherit(u, { className: "string" }),
        { className: "string", begin: /<.*?>/ },
        n,
        e.C_BLOCK_COMMENT_MODE,
      ],
    },
    f = { className: "title", begin: t.optional(i) + e.IDENT_RE, relevance: 0 },
    p = t.optional(i) + e.IDENT_RE + "\\s*\\(",
    E = {
      keyword: [
        "asm",
        "auto",
        "break",
        "case",
        "continue",
        "default",
        "do",
        "else",
        "enum",
        "extern",
        "for",
        "fortran",
        "goto",
        "if",
        "inline",
        "register",
        "restrict",
        "return",
        "sizeof",
        "typeof",
        "typeof_unqual",
        "struct",
        "switch",
        "typedef",
        "union",
        "volatile",
        "while",
        "_Alignas",
        "_Alignof",
        "_Atomic",
        "_Generic",
        "_Noreturn",
        "_Static_assert",
        "_Thread_local",
        "alignas",
        "alignof",
        "noreturn",
        "static_assert",
        "thread_local",
        "_Pragma",
      ],
      type: [
        "float",
        "double",
        "signed",
        "unsigned",
        "int",
        "short",
        "long",
        "char",
        "void",
        "_Bool",
        "_BitInt",
        "_Complex",
        "_Imaginary",
        "_Decimal32",
        "_Decimal64",
        "_Decimal96",
        "_Decimal128",
        "_Decimal64x",
        "_Decimal128x",
        "_Float16",
        "_Float32",
        "_Float64",
        "_Float128",
        "_Float32x",
        "_Float64x",
        "_Float128x",
        "const",
        "static",
        "constexpr",
        "complex",
        "bool",
        "imaginary",
      ],
      literal: "true false NULL",
      built_in:
        "std string wstring cin cout cerr clog stdin stdout stderr stringstream istringstream ostringstream auto_ptr deque list queue stack vector map set pair bitset multiset multimap unordered_set unordered_map unordered_multiset unordered_multimap priority_queue make_pair array shared_ptr abort terminate abs acos asin atan2 atan calloc ceil cosh cos exit exp fabs floor fmod fprintf fputs free frexp fscanf future isalnum isalpha iscntrl isdigit isgraph islower isprint ispunct isspace isupper isxdigit tolower toupper labs ldexp log10 log malloc realloc memchr memcmp memcpy memset modf pow printf putchar puts scanf sinh sin snprintf sprintf sqrt sscanf strcat strchr strcmp strcpy strcspn strlen strncat strncmp strncpy strpbrk strrchr strspn strstr tanh tan vfprintf vprintf vsprintf endl initializer_list unique_ptr",
    },
    h = [c, a, n, e.C_BLOCK_COMMENT_MODE, d, u],
    m = {
      variants: [
        { begin: /=/, end: /;/ },
        { begin: /\(/, end: /\)/ },
        { beginKeywords: "new throw return else", end: /;/ },
      ],
      keywords: E,
      contains: h.concat([
        {
          begin: /\(/,
          end: /\)/,
          keywords: E,
          contains: h.concat(["self"]),
          relevance: 0,
        },
      ]),
      relevance: 0,
    },
    b = {
      begin: "(" + l + "[\\*&\\s]+)+" + p,
      returnBegin: !0,
      end: /[{;=]/,
      excludeEnd: !0,
      keywords: E,
      illegal: /[^\w\s\*&:<>.]/,
      contains: [
        { begin: r, keywords: E, relevance: 0 },
        {
          begin: p,
          returnBegin: !0,
          contains: [e.inherit(f, { className: "title.function" })],
          relevance: 0,
        },
        { relevance: 0, match: /,/ },
        {
          className: "params",
          begin: /\(/,
          end: /\)/,
          keywords: E,
          relevance: 0,
          contains: [
            n,
            e.C_BLOCK_COMMENT_MODE,
            u,
            d,
            a,
            {
              begin: /\(/,
              end: /\)/,
              keywords: E,
              relevance: 0,
              contains: ["self", n, e.C_BLOCK_COMMENT_MODE, u, d, a],
            },
          ],
        },
        a,
        n,
        e.C_BLOCK_COMMENT_MODE,
        c,
      ],
    };
  return {
    name: "C",
    aliases: ["h"],
    keywords: E,
    disableAutodetect: !0,
    illegal: "</",
    contains: [].concat(m, b, h, [
      c,
      { begin: e.IDENT_RE + "::", keywords: E },
      {
        className: "class",
        beginKeywords: "enum class struct union",
        end: /[{;:<>=]/,
        contains: [{ beginKeywords: "final class struct" }, e.TITLE_MODE],
      },
    ]),
    exports: { preprocessor: c, strings: u, keywords: E },
  };
}
function JN(e) {
  const t = e.regex,
    n = e.COMMENT("//", "$", { contains: [{ begin: /\\\n/ }] }),
    r = "decltype\\(auto\\)",
    i = "[a-zA-Z_]\\w*::",
    l =
      "(?!struct)(" +
      r +
      "|" +
      t.optional(i) +
      "[a-zA-Z_]\\w*" +
      t.optional("<[^<>]+>") +
      ")",
    a = { className: "type", begin: "\\b[a-z\\d_]*_t\\b" },
    u = {
      className: "string",
      variants: [
        {
          begin: '(u8?|U|L)?"',
          end: '"',
          illegal: "\\n",
          contains: [e.BACKSLASH_ESCAPE],
        },
        {
          begin:
            "(u8?|U|L)?'(" +
            "\\\\(x[0-9A-Fa-f]{2}|u[0-9A-Fa-f]{4,8}|[0-7]{3}|\\S)" +
            "|.)",
          end: "'",
          illegal: ".",
        },
        e.END_SAME_AS_BEGIN({
          begin: /(?:u8?|U|L)?R"([^()\\ ]{0,16})\(/,
          end: /\)([^()\\ ]{0,16})"/,
        }),
      ],
    },
    d = {
      className: "number",
      variants: [
        {
          begin:
            "[+-]?(?:(?:[0-9](?:'?[0-9])*\\.(?:[0-9](?:'?[0-9])*)?|\\.[0-9](?:'?[0-9])*)(?:[Ee][+-]?[0-9](?:'?[0-9])*)?|[0-9](?:'?[0-9])*[Ee][+-]?[0-9](?:'?[0-9])*|0[Xx](?:[0-9A-Fa-f](?:'?[0-9A-Fa-f])*(?:\\.(?:[0-9A-Fa-f](?:'?[0-9A-Fa-f])*)?)?|\\.[0-9A-Fa-f](?:'?[0-9A-Fa-f])*)[Pp][+-]?[0-9](?:'?[0-9])*)(?:[Ff](?:16|32|64|128)?|(BF|bf)16|[Ll]|)",
        },
        {
          begin:
            "[+-]?\\b(?:0[Bb][01](?:'?[01])*|0[Xx][0-9A-Fa-f](?:'?[0-9A-Fa-f])*|0(?:'?[0-7])*|[1-9](?:'?[0-9])*)(?:[Uu](?:LL?|ll?)|[Uu][Zz]?|(?:LL?|ll?)[Uu]?|[Zz][Uu]|)",
        },
      ],
      relevance: 0,
    },
    c = {
      className: "meta",
      begin: /#\s*[a-z]+\b/,
      end: /$/,
      keywords: {
        keyword:
          "if else elif endif define undef warning error line pragma _Pragma ifdef ifndef include",
      },
      contains: [
        { begin: /\\\n/, relevance: 0 },
        e.inherit(u, { className: "string" }),
        { className: "string", begin: /<.*?>/ },
        n,
        e.C_BLOCK_COMMENT_MODE,
      ],
    },
    f = { className: "title", begin: t.optional(i) + e.IDENT_RE, relevance: 0 },
    p = t.optional(i) + e.IDENT_RE + "\\s*\\(",
    g = [
      "alignas",
      "alignof",
      "and",
      "and_eq",
      "asm",
      "atomic_cancel",
      "atomic_commit",
      "atomic_noexcept",
      "auto",
      "bitand",
      "bitor",
      "break",
      "case",
      "catch",
      "class",
      "co_await",
      "co_return",
      "co_yield",
      "compl",
      "concept",
      "const_cast|10",
      "consteval",
      "constexpr",
      "constinit",
      "continue",
      "decltype",
      "default",
      "delete",
      "do",
      "dynamic_cast|10",
      "else",
      "enum",
      "explicit",
      "export",
      "extern",
      "false",
      "final",
      "for",
      "friend",
      "goto",
      "if",
      "import",
      "inline",
      "module",
      "mutable",
      "namespace",
      "new",
      "noexcept",
      "not",
      "not_eq",
      "nullptr",
      "operator",
      "or",
      "or_eq",
      "override",
      "private",
      "protected",
      "public",
      "reflexpr",
      "register",
      "reinterpret_cast|10",
      "requires",
      "return",
      "sizeof",
      "static_assert",
      "static_cast|10",
      "struct",
      "switch",
      "synchronized",
      "template",
      "this",
      "thread_local",
      "throw",
      "transaction_safe",
      "transaction_safe_dynamic",
      "true",
      "try",
      "typedef",
      "typeid",
      "typename",
      "union",
      "using",
      "virtual",
      "volatile",
      "while",
      "xor",
      "xor_eq",
    ],
    y = [
      "bool",
      "char",
      "char16_t",
      "char32_t",
      "char8_t",
      "double",
      "float",
      "int",
      "long",
      "short",
      "void",
      "wchar_t",
      "unsigned",
      "signed",
      "const",
      "static",
    ],
    E = [
      "any",
      "auto_ptr",
      "barrier",
      "binary_semaphore",
      "bitset",
      "complex",
      "condition_variable",
      "condition_variable_any",
      "counting_semaphore",
      "deque",
      "false_type",
      "flat_map",
      "flat_set",
      "future",
      "imaginary",
      "initializer_list",
      "istringstream",
      "jthread",
      "latch",
      "lock_guard",
      "multimap",
      "multiset",
      "mutex",
      "optional",
      "ostringstream",
      "packaged_task",
      "pair",
      "promise",
      "priority_queue",
      "queue",
      "recursive_mutex",
      "recursive_timed_mutex",
      "scoped_lock",
      "set",
      "shared_future",
      "shared_lock",
      "shared_mutex",
      "shared_timed_mutex",
      "shared_ptr",
      "stack",
      "string_view",
      "stringstream",
      "timed_mutex",
      "thread",
      "true_type",
      "tuple",
      "unique_lock",
      "unique_ptr",
      "unordered_map",
      "unordered_multimap",
      "unordered_multiset",
      "unordered_set",
      "variant",
      "vector",
      "weak_ptr",
      "wstring",
      "wstring_view",
    ],
    h = [
      "abort",
      "abs",
      "acos",
      "apply",
      "as_const",
      "asin",
      "atan",
      "atan2",
      "calloc",
      "ceil",
      "cerr",
      "cin",
      "clog",
      "cos",
      "cosh",
      "cout",
      "declval",
      "endl",
      "exchange",
      "exit",
      "exp",
      "fabs",
      "floor",
      "fmod",
      "forward",
      "fprintf",
      "fputs",
      "free",
      "frexp",
      "fscanf",
      "future",
      "invoke",
      "isalnum",
      "isalpha",
      "iscntrl",
      "isdigit",
      "isgraph",
      "islower",
      "isprint",
      "ispunct",
      "isspace",
      "isupper",
      "isxdigit",
      "labs",
      "launder",
      "ldexp",
      "log",
      "log10",
      "make_pair",
      "make_shared",
      "make_shared_for_overwrite",
      "make_tuple",
      "make_unique",
      "malloc",
      "memchr",
      "memcmp",
      "memcpy",
      "memset",
      "modf",
      "move",
      "pow",
      "printf",
      "putchar",
      "puts",
      "realloc",
      "scanf",
      "sin",
      "sinh",
      "snprintf",
      "sprintf",
      "sqrt",
      "sscanf",
      "std",
      "stderr",
      "stdin",
      "stdout",
      "strcat",
      "strchr",
      "strcmp",
      "strcpy",
      "strcspn",
      "strlen",
      "strncat",
      "strncmp",
      "strncpy",
      "strpbrk",
      "strrchr",
      "strspn",
      "strstr",
      "swap",
      "tan",
      "tanh",
      "terminate",
      "to_underlying",
      "tolower",
      "toupper",
      "vfprintf",
      "visit",
      "vprintf",
      "vsprintf",
    ],
    _ = {
      type: y,
      keyword: g,
      literal: ["NULL", "false", "nullopt", "nullptr", "true"],
      built_in: ["_Pragma"],
      _type_hints: E,
    },
    N = {
      className: "function.dispatch",
      relevance: 0,
      keywords: { _hint: h },
      begin: t.concat(
        /\b/,
        /(?!decltype)/,
        /(?!if)/,
        /(?!for)/,
        /(?!switch)/,
        /(?!while)/,
        e.IDENT_RE,
        t.lookahead(/(<[^<>]+>|)\s*\(/),
      ),
    },
    x = [N, c, a, n, e.C_BLOCK_COMMENT_MODE, d, u],
    O = {
      variants: [
        { begin: /=/, end: /;/ },
        { begin: /\(/, end: /\)/ },
        { beginKeywords: "new throw return else", end: /;/ },
      ],
      keywords: _,
      contains: x.concat([
        {
          begin: /\(/,
          end: /\)/,
          keywords: _,
          contains: x.concat(["self"]),
          relevance: 0,
        },
      ]),
      relevance: 0,
    },
    I = {
      className: "function",
      begin: "(" + l + "[\\*&\\s]+)+" + p,
      returnBegin: !0,
      end: /[{;=]/,
      excludeEnd: !0,
      keywords: _,
      illegal: /[^\w\s\*&:<>.]/,
      contains: [
        { begin: r, keywords: _, relevance: 0 },
        { begin: p, returnBegin: !0, contains: [f], relevance: 0 },
        { begin: /::/, relevance: 0 },
        { begin: /:/, endsWithParent: !0, contains: [u, d] },
        { relevance: 0, match: /,/ },
        {
          className: "params",
          begin: /\(/,
          end: /\)/,
          keywords: _,
          relevance: 0,
          contains: [
            n,
            e.C_BLOCK_COMMENT_MODE,
            u,
            d,
            a,
            {
              begin: /\(/,
              end: /\)/,
              keywords: _,
              relevance: 0,
              contains: ["self", n, e.C_BLOCK_COMMENT_MODE, u, d, a],
            },
          ],
        },
        a,
        n,
        e.C_BLOCK_COMMENT_MODE,
        c,
      ],
    };
  return {
    name: "C++",
    aliases: ["cc", "c++", "h++", "hpp", "hh", "hxx", "cxx"],
    keywords: _,
    illegal: "</",
    classNameAliases: { "function.dispatch": "built_in" },
    contains: [].concat(O, I, N, x, [
      c,
      {
        begin:
          "\\b(deque|list|queue|priority_queue|pair|stack|vector|map|set|bitset|multiset|multimap|unordered_map|unordered_set|unordered_multiset|unordered_multimap|array|tuple|optional|variant|function|flat_map|flat_set)\\s*<(?!<)",
        end: ">",
        keywords: _,
        contains: ["self", a],
      },
      { begin: e.IDENT_RE + "::", keywords: _ },
      {
        match: [
          /\b(?:enum(?:\s+(?:class|struct))?|class|struct|union)/,
          /\s+/,
          /\w+/,
        ],
        className: { 1: "keyword", 3: "title.class" },
      },
    ]),
  };
}
function eC(e) {
  const t = [
      "bool",
      "byte",
      "char",
      "decimal",
      "delegate",
      "double",
      "dynamic",
      "enum",
      "float",
      "int",
      "long",
      "nint",
      "nuint",
      "object",
      "sbyte",
      "short",
      "string",
      "ulong",
      "uint",
      "ushort",
    ],
    n = [
      "public",
      "private",
      "protected",
      "static",
      "internal",
      "protected",
      "abstract",
      "async",
      "extern",
      "override",
      "unsafe",
      "virtual",
      "new",
      "sealed",
      "partial",
    ],
    r = ["default", "false", "null", "true"],
    i = [
      "abstract",
      "as",
      "base",
      "break",
      "case",
      "catch",
      "class",
      "const",
      "continue",
      "do",
      "else",
      "event",
      "explicit",
      "extern",
      "finally",
      "fixed",
      "for",
      "foreach",
      "goto",
      "if",
      "implicit",
      "in",
      "interface",
      "internal",
      "is",
      "lock",
      "namespace",
      "new",
      "operator",
      "out",
      "override",
      "params",
      "private",
      "protected",
      "public",
      "readonly",
      "record",
      "ref",
      "return",
      "scoped",
      "sealed",
      "sizeof",
      "stackalloc",
      "static",
      "struct",
      "switch",
      "this",
      "throw",
      "try",
      "typeof",
      "unchecked",
      "unsafe",
      "using",
      "virtual",
      "void",
      "volatile",
      "while",
    ],
    o = [
      "add",
      "alias",
      "and",
      "ascending",
      "args",
      "async",
      "await",
      "by",
      "descending",
      "dynamic",
      "equals",
      "file",
      "from",
      "get",
      "global",
      "group",
      "init",
      "into",
      "join",
      "let",
      "nameof",
      "not",
      "notnull",
      "on",
      "or",
      "orderby",
      "partial",
      "record",
      "remove",
      "required",
      "scoped",
      "select",
      "set",
      "unmanaged",
      "value|0",
      "var",
      "when",
      "where",
      "with",
      "yield",
    ],
    l = { keyword: i.concat(o), built_in: t, literal: r },
    a = e.inherit(e.TITLE_MODE, { begin: "[a-zA-Z](\\.?\\w)*" }),
    s = {
      className: "number",
      variants: [
        { begin: "\\b(0b[01']+)" },
        {
          begin:
            "(-?)\\b([\\d']+(\\.[\\d']*)?|\\.[\\d']+)(u|U|l|L|ul|UL|f|F|b|B)",
        },
        {
          begin:
            "(-?)(\\b0[xX][a-fA-F0-9']+|(\\b[\\d']+(\\.[\\d']*)?|\\.[\\d']+)([eE][-+]?[\\d']+)?)",
        },
      ],
      relevance: 0,
    },
    u = {
      className: "string",
      begin: /"""("*)(?!")(.|\n)*?"""\1/,
      relevance: 1,
    },
    d = {
      className: "string",
      begin: '@"',
      end: '"',
      contains: [{ begin: '""' }],
    },
    c = e.inherit(d, { illegal: /\n/ }),
    f = { className: "subst", begin: /\{/, end: /\}/, keywords: l },
    p = e.inherit(f, { illegal: /\n/ }),
    g = {
      className: "string",
      begin: /\$"/,
      end: '"',
      illegal: /\n/,
      contains: [{ begin: /\{\{/ }, { begin: /\}\}/ }, e.BACKSLASH_ESCAPE, p],
    },
    y = {
      className: "string",
      begin: /\$@"/,
      end: '"',
      contains: [{ begin: /\{\{/ }, { begin: /\}\}/ }, { begin: '""' }, f],
    },
    E = e.inherit(y, {
      illegal: /\n/,
      contains: [{ begin: /\{\{/ }, { begin: /\}\}/ }, { begin: '""' }, p],
    });
  ((f.contains = [
    y,
    g,
    d,
    e.APOS_STRING_MODE,
    e.QUOTE_STRING_MODE,
    s,
    e.C_BLOCK_COMMENT_MODE,
  ]),
    (p.contains = [
      E,
      g,
      c,
      e.APOS_STRING_MODE,
      e.QUOTE_STRING_MODE,
      s,
      e.inherit(e.C_BLOCK_COMMENT_MODE, { illegal: /\n/ }),
    ]));
  const h = { variants: [u, y, g, d, e.APOS_STRING_MODE, e.QUOTE_STRING_MODE] },
    m = { begin: "<", end: ">", contains: [{ beginKeywords: "in out" }, a] },
    b =
      e.IDENT_RE +
      "(<" +
      e.IDENT_RE +
      "(\\s*,\\s*" +
      e.IDENT_RE +
      ")*>)?(\\[\\])?",
    _ = { begin: "@" + e.IDENT_RE, relevance: 0 };
  return {
    name: "C#",
    aliases: ["cs", "c#"],
    keywords: l,
    illegal: /::/,
    contains: [
      e.COMMENT("///", "$", {
        returnBegin: !0,
        contains: [
          {
            className: "doctag",
            variants: [
              { begin: "///", relevance: 0 },
              { begin: "<!--|-->" },
              { begin: "</?", end: ">" },
            ],
          },
        ],
      }),
      e.C_LINE_COMMENT_MODE,
      e.C_BLOCK_COMMENT_MODE,
      {
        className: "meta",
        begin: "#",
        end: "$",
        keywords: {
          keyword:
            "if else elif endif define undef warning error line region endregion pragma checksum",
        },
      },
      h,
      s,
      {
        beginKeywords: "class interface",
        relevance: 0,
        end: /[{;=]/,
        illegal: /[^\s:,]/,
        contains: [
          { beginKeywords: "where class" },
          a,
          m,
          e.C_LINE_COMMENT_MODE,
          e.C_BLOCK_COMMENT_MODE,
        ],
      },
      {
        beginKeywords: "namespace",
        relevance: 0,
        end: /[{;=]/,
        illegal: /[^\s:]/,
        contains: [a, e.C_LINE_COMMENT_MODE, e.C_BLOCK_COMMENT_MODE],
      },
      {
        beginKeywords: "record",
        relevance: 0,
        end: /[{;=]/,
        illegal: /[^\s:]/,
        contains: [a, m, e.C_LINE_COMMENT_MODE, e.C_BLOCK_COMMENT_MODE],
      },
      {
        className: "meta",
        begin: "^\\s*\\[(?=[\\w])",
        excludeBegin: !0,
        end: "\\]",
        excludeEnd: !0,
        contains: [{ className: "string", begin: /"/, end: /"/ }],
      },
      { beginKeywords: "new return throw await else", relevance: 0 },
      {
        className: "function",
        begin: "(" + b + "\\s+)+" + e.IDENT_RE + "\\s*(<[^=]+>\\s*)?\\(",
        returnBegin: !0,
        end: /\s*[{;=]/,
        excludeEnd: !0,
        keywords: l,
        contains: [
          { beginKeywords: n.join(" "), relevance: 0 },
          {
            begin: e.IDENT_RE + "\\s*(<[^=]+>\\s*)?\\(",
            returnBegin: !0,
            contains: [e.TITLE_MODE, m],
            relevance: 0,
          },
          { match: /\(\)/ },
          {
            className: "params",
            begin: /\(/,
            end: /\)/,
            excludeBegin: !0,
            excludeEnd: !0,
            keywords: l,
            relevance: 0,
            contains: [h, s, e.C_BLOCK_COMMENT_MODE],
          },
          e.C_LINE_COMMENT_MODE,
          e.C_BLOCK_COMMENT_MODE,
        ],
      },
      _,
    ],
  };
}
const tC = (e) => ({
    IMPORTANT: { scope: "meta", begin: "!important" },
    BLOCK_COMMENT: e.C_BLOCK_COMMENT_MODE,
    HEXCOLOR: {
      scope: "number",
      begin: /#(([0-9a-fA-F]{3,4})|(([0-9a-fA-F]{2}){3,4}))\b/,
    },
    FUNCTION_DISPATCH: { className: "built_in", begin: /[\w-]+(?=\()/ },
    ATTRIBUTE_SELECTOR_MODE: {
      scope: "selector-attr",
      begin: /\[/,
      end: /\]/,
      illegal: "$",
      contains: [e.APOS_STRING_MODE, e.QUOTE_STRING_MODE],
    },
    CSS_NUMBER_MODE: {
      scope: "number",
      begin:
        e.NUMBER_RE +
        "(%|em|ex|ch|rem|vw|vh|vmin|vmax|cm|mm|in|pt|pc|px|deg|grad|rad|turn|s|ms|Hz|kHz|dpi|dpcm|dppx)?",
      relevance: 0,
    },
    CSS_VARIABLE: { className: "attr", begin: /--[A-Za-z_][A-Za-z0-9_-]*/ },
  }),
  nC = [
    "a",
    "abbr",
    "address",
    "article",
    "aside",
    "audio",
    "b",
    "blockquote",
    "body",
    "button",
    "canvas",
    "caption",
    "cite",
    "code",
    "dd",
    "del",
    "details",
    "dfn",
    "div",
    "dl",
    "dt",
    "em",
    "fieldset",
    "figcaption",
    "figure",
    "footer",
    "form",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "header",
    "hgroup",
    "html",
    "i",
    "iframe",
    "img",
    "input",
    "ins",
    "kbd",
    "label",
    "legend",
    "li",
    "main",
    "mark",
    "menu",
    "nav",
    "object",
    "ol",
    "optgroup",
    "option",
    "p",
    "picture",
    "q",
    "quote",
    "samp",
    "section",
    "select",
    "source",
    "span",
    "strong",
    "summary",
    "sup",
    "table",
    "tbody",
    "td",
    "textarea",
    "tfoot",
    "th",
    "thead",
    "time",
    "tr",
    "ul",
    "var",
    "video",
  ],
  rC = [
    "defs",
    "g",
    "marker",
    "mask",
    "pattern",
    "svg",
    "switch",
    "symbol",
    "feBlend",
    "feColorMatrix",
    "feComponentTransfer",
    "feComposite",
    "feConvolveMatrix",
    "feDiffuseLighting",
    "feDisplacementMap",
    "feFlood",
    "feGaussianBlur",
    "feImage",
    "feMerge",
    "feMorphology",
    "feOffset",
    "feSpecularLighting",
    "feTile",
    "feTurbulence",
    "linearGradient",
    "radialGradient",
    "stop",
    "circle",
    "ellipse",
    "image",
    "line",
    "path",
    "polygon",
    "polyline",
    "rect",
    "text",
    "use",
    "textPath",
    "tspan",
    "foreignObject",
    "clipPath",
  ],
  iC = [...nC, ...rC],
  oC = [
    "any-hover",
    "any-pointer",
    "aspect-ratio",
    "color",
    "color-gamut",
    "color-index",
    "device-aspect-ratio",
    "device-height",
    "device-width",
    "display-mode",
    "forced-colors",
    "grid",
    "height",
    "hover",
    "inverted-colors",
    "monochrome",
    "orientation",
    "overflow-block",
    "overflow-inline",
    "pointer",
    "prefers-color-scheme",
    "prefers-contrast",
    "prefers-reduced-motion",
    "prefers-reduced-transparency",
    "resolution",
    "scan",
    "scripting",
    "update",
    "width",
    "min-width",
    "max-width",
    "min-height",
    "max-height",
  ]
    .sort()
    .reverse(),
  lC = [
    "active",
    "any-link",
    "blank",
    "checked",
    "current",
    "default",
    "defined",
    "dir",
    "disabled",
    "drop",
    "empty",
    "enabled",
    "first",
    "first-child",
    "first-of-type",
    "fullscreen",
    "future",
    "focus",
    "focus-visible",
    "focus-within",
    "has",
    "host",
    "host-context",
    "hover",
    "indeterminate",
    "in-range",
    "invalid",
    "is",
    "lang",
    "last-child",
    "last-of-type",
    "left",
    "link",
    "local-link",
    "not",
    "nth-child",
    "nth-col",
    "nth-last-child",
    "nth-last-col",
    "nth-last-of-type",
    "nth-of-type",
    "only-child",
    "only-of-type",
    "optional",
    "out-of-range",
    "past",
    "placeholder-shown",
    "read-only",
    "read-write",
    "required",
    "right",
    "root",
    "scope",
    "target",
    "target-within",
    "user-invalid",
    "valid",
    "visited",
    "where",
  ]
    .sort()
    .reverse(),
  aC = [
    "after",
    "backdrop",
    "before",
    "cue",
    "cue-region",
    "first-letter",
    "first-line",
    "grammar-error",
    "marker",
    "part",
    "placeholder",
    "selection",
    "slotted",
    "spelling-error",
  ]
    .sort()
    .reverse(),
  sC = [
    "accent-color",
    "align-content",
    "align-items",
    "align-self",
    "alignment-baseline",
    "all",
    "anchor-name",
    "animation",
    "animation-composition",
    "animation-delay",
    "animation-direction",
    "animation-duration",
    "animation-fill-mode",
    "animation-iteration-count",
    "animation-name",
    "animation-play-state",
    "animation-range",
    "animation-range-end",
    "animation-range-start",
    "animation-timeline",
    "animation-timing-function",
    "appearance",
    "aspect-ratio",
    "backdrop-filter",
    "backface-visibility",
    "background",
    "background-attachment",
    "background-blend-mode",
    "background-clip",
    "background-color",
    "background-image",
    "background-origin",
    "background-position",
    "background-position-x",
    "background-position-y",
    "background-repeat",
    "background-size",
    "baseline-shift",
    "block-size",
    "border",
    "border-block",
    "border-block-color",
    "border-block-end",
    "border-block-end-color",
    "border-block-end-style",
    "border-block-end-width",
    "border-block-start",
    "border-block-start-color",
    "border-block-start-style",
    "border-block-start-width",
    "border-block-style",
    "border-block-width",
    "border-bottom",
    "border-bottom-color",
    "border-bottom-left-radius",
    "border-bottom-right-radius",
    "border-bottom-style",
    "border-bottom-width",
    "border-collapse",
    "border-color",
    "border-end-end-radius",
    "border-end-start-radius",
    "border-image",
    "border-image-outset",
    "border-image-repeat",
    "border-image-slice",
    "border-image-source",
    "border-image-width",
    "border-inline",
    "border-inline-color",
    "border-inline-end",
    "border-inline-end-color",
    "border-inline-end-style",
    "border-inline-end-width",
    "border-inline-start",
    "border-inline-start-color",
    "border-inline-start-style",
    "border-inline-start-width",
    "border-inline-style",
    "border-inline-width",
    "border-left",
    "border-left-color",
    "border-left-style",
    "border-left-width",
    "border-radius",
    "border-right",
    "border-right-color",
    "border-right-style",
    "border-right-width",
    "border-spacing",
    "border-start-end-radius",
    "border-start-start-radius",
    "border-style",
    "border-top",
    "border-top-color",
    "border-top-left-radius",
    "border-top-right-radius",
    "border-top-style",
    "border-top-width",
    "border-width",
    "bottom",
    "box-align",
    "box-decoration-break",
    "box-direction",
    "box-flex",
    "box-flex-group",
    "box-lines",
    "box-ordinal-group",
    "box-orient",
    "box-pack",
    "box-shadow",
    "box-sizing",
    "break-after",
    "break-before",
    "break-inside",
    "caption-side",
    "caret-color",
    "clear",
    "clip",
    "clip-path",
    "clip-rule",
    "color",
    "color-interpolation",
    "color-interpolation-filters",
    "color-profile",
    "color-rendering",
    "color-scheme",
    "column-count",
    "column-fill",
    "column-gap",
    "column-rule",
    "column-rule-color",
    "column-rule-style",
    "column-rule-width",
    "column-span",
    "column-width",
    "columns",
    "contain",
    "contain-intrinsic-block-size",
    "contain-intrinsic-height",
    "contain-intrinsic-inline-size",
    "contain-intrinsic-size",
    "contain-intrinsic-width",
    "container",
    "container-name",
    "container-type",
    "content",
    "content-visibility",
    "counter-increment",
    "counter-reset",
    "counter-set",
    "cue",
    "cue-after",
    "cue-before",
    "cursor",
    "cx",
    "cy",
    "direction",
    "display",
    "dominant-baseline",
    "empty-cells",
    "enable-background",
    "field-sizing",
    "fill",
    "fill-opacity",
    "fill-rule",
    "filter",
    "flex",
    "flex-basis",
    "flex-direction",
    "flex-flow",
    "flex-grow",
    "flex-shrink",
    "flex-wrap",
    "float",
    "flood-color",
    "flood-opacity",
    "flow",
    "font",
    "font-display",
    "font-family",
    "font-feature-settings",
    "font-kerning",
    "font-language-override",
    "font-optical-sizing",
    "font-palette",
    "font-size",
    "font-size-adjust",
    "font-smooth",
    "font-smoothing",
    "font-stretch",
    "font-style",
    "font-synthesis",
    "font-synthesis-position",
    "font-synthesis-small-caps",
    "font-synthesis-style",
    "font-synthesis-weight",
    "font-variant",
    "font-variant-alternates",
    "font-variant-caps",
    "font-variant-east-asian",
    "font-variant-emoji",
    "font-variant-ligatures",
    "font-variant-numeric",
    "font-variant-position",
    "font-variation-settings",
    "font-weight",
    "forced-color-adjust",
    "gap",
    "glyph-orientation-horizontal",
    "glyph-orientation-vertical",
    "grid",
    "grid-area",
    "grid-auto-columns",
    "grid-auto-flow",
    "grid-auto-rows",
    "grid-column",
    "grid-column-end",
    "grid-column-start",
    "grid-gap",
    "grid-row",
    "grid-row-end",
    "grid-row-start",
    "grid-template",
    "grid-template-areas",
    "grid-template-columns",
    "grid-template-rows",
    "hanging-punctuation",
    "height",
    "hyphenate-character",
    "hyphenate-limit-chars",
    "hyphens",
    "icon",
    "image-orientation",
    "image-rendering",
    "image-resolution",
    "ime-mode",
    "initial-letter",
    "initial-letter-align",
    "inline-size",
    "inset",
    "inset-area",
    "inset-block",
    "inset-block-end",
    "inset-block-start",
    "inset-inline",
    "inset-inline-end",
    "inset-inline-start",
    "isolation",
    "justify-content",
    "justify-items",
    "justify-self",
    "kerning",
    "left",
    "letter-spacing",
    "lighting-color",
    "line-break",
    "line-height",
    "line-height-step",
    "list-style",
    "list-style-image",
    "list-style-position",
    "list-style-type",
    "margin",
    "margin-block",
    "margin-block-end",
    "margin-block-start",
    "margin-bottom",
    "margin-inline",
    "margin-inline-end",
    "margin-inline-start",
    "margin-left",
    "margin-right",
    "margin-top",
    "margin-trim",
    "marker",
    "marker-end",
    "marker-mid",
    "marker-start",
    "marks",
    "mask",
    "mask-border",
    "mask-border-mode",
    "mask-border-outset",
    "mask-border-repeat",
    "mask-border-slice",
    "mask-border-source",
    "mask-border-width",
    "mask-clip",
    "mask-composite",
    "mask-image",
    "mask-mode",
    "mask-origin",
    "mask-position",
    "mask-repeat",
    "mask-size",
    "mask-type",
    "masonry-auto-flow",
    "math-depth",
    "math-shift",
    "math-style",
    "max-block-size",
    "max-height",
    "max-inline-size",
    "max-width",
    "min-block-size",
    "min-height",
    "min-inline-size",
    "min-width",
    "mix-blend-mode",
    "nav-down",
    "nav-index",
    "nav-left",
    "nav-right",
    "nav-up",
    "none",
    "normal",
    "object-fit",
    "object-position",
    "offset",
    "offset-anchor",
    "offset-distance",
    "offset-path",
    "offset-position",
    "offset-rotate",
    "opacity",
    "order",
    "orphans",
    "outline",
    "outline-color",
    "outline-offset",
    "outline-style",
    "outline-width",
    "overflow",
    "overflow-anchor",
    "overflow-block",
    "overflow-clip-margin",
    "overflow-inline",
    "overflow-wrap",
    "overflow-x",
    "overflow-y",
    "overlay",
    "overscroll-behavior",
    "overscroll-behavior-block",
    "overscroll-behavior-inline",
    "overscroll-behavior-x",
    "overscroll-behavior-y",
    "padding",
    "padding-block",
    "padding-block-end",
    "padding-block-start",
    "padding-bottom",
    "padding-inline",
    "padding-inline-end",
    "padding-inline-start",
    "padding-left",
    "padding-right",
    "padding-top",
    "page",
    "page-break-after",
    "page-break-before",
    "page-break-inside",
    "paint-order",
    "pause",
    "pause-after",
    "pause-before",
    "perspective",
    "perspective-origin",
    "place-content",
    "place-items",
    "place-self",
    "pointer-events",
    "position",
    "position-anchor",
    "position-visibility",
    "print-color-adjust",
    "quotes",
    "r",
    "resize",
    "rest",
    "rest-after",
    "rest-before",
    "right",
    "rotate",
    "row-gap",
    "ruby-align",
    "ruby-position",
    "scale",
    "scroll-behavior",
    "scroll-margin",
    "scroll-margin-block",
    "scroll-margin-block-end",
    "scroll-margin-block-start",
    "scroll-margin-bottom",
    "scroll-margin-inline",
    "scroll-margin-inline-end",
    "scroll-margin-inline-start",
    "scroll-margin-left",
    "scroll-margin-right",
    "scroll-margin-top",
    "scroll-padding",
    "scroll-padding-block",
    "scroll-padding-block-end",
    "scroll-padding-block-start",
    "scroll-padding-bottom",
    "scroll-padding-inline",
    "scroll-padding-inline-end",
    "scroll-padding-inline-start",
    "scroll-padding-left",
    "scroll-padding-right",
    "scroll-padding-top",
    "scroll-snap-align",
    "scroll-snap-stop",
    "scroll-snap-type",
    "scroll-timeline",
    "scroll-timeline-axis",
    "scroll-timeline-name",
    "scrollbar-color",
    "scrollbar-gutter",
    "scrollbar-width",
    "shape-image-threshold",
    "shape-margin",
    "shape-outside",
    "shape-rendering",
    "speak",
    "speak-as",
    "src",
    "stop-color",
    "stop-opacity",
    "stroke",
    "stroke-dasharray",
    "stroke-dashoffset",
    "stroke-linecap",
    "stroke-linejoin",
    "stroke-miterlimit",
    "stroke-opacity",
    "stroke-width",
    "tab-size",
    "table-layout",
    "text-align",
    "text-align-all",
    "text-align-last",
    "text-anchor",
    "text-combine-upright",
    "text-decoration",
    "text-decoration-color",
    "text-decoration-line",
    "text-decoration-skip",
    "text-decoration-skip-ink",
    "text-decoration-style",
    "text-decoration-thickness",
    "text-emphasis",
    "text-emphasis-color",
    "text-emphasis-position",
    "text-emphasis-style",
    "text-indent",
    "text-justify",
    "text-orientation",
    "text-overflow",
    "text-rendering",
    "text-shadow",
    "text-size-adjust",
    "text-transform",
    "text-underline-offset",
    "text-underline-position",
    "text-wrap",
    "text-wrap-mode",
    "text-wrap-style",
    "timeline-scope",
    "top",
    "touch-action",
    "transform",
    "transform-box",
    "transform-origin",
    "transform-style",
    "transition",
    "transition-behavior",
    "transition-delay",
    "transition-duration",
    "transition-property",
    "transition-timing-function",
    "translate",
    "unicode-bidi",
    "user-modify",
    "user-select",
    "vector-effect",
    "vertical-align",
    "view-timeline",
    "view-timeline-axis",
    "view-timeline-inset",
    "view-timeline-name",
    "view-transition-name",
    "visibility",
    "voice-balance",
    "voice-duration",
    "voice-family",
    "voice-pitch",
    "voice-range",
    "voice-rate",
    "voice-stress",
    "voice-volume",
    "white-space",
    "white-space-collapse",
    "widows",
    "width",
    "will-change",
    "word-break",
    "word-spacing",
    "word-wrap",
    "writing-mode",
    "x",
    "y",
    "z-index",
    "zoom",
  ]
    .sort()
    .reverse();
function uC(e) {
  const t = e.regex,
    n = tC(e),
    r = { begin: /-(webkit|moz|ms|o)-(?=[a-z])/ },
    i = "and or not only",
    o = /@-?\w[\w]*(-\w+)*/,
    l = "[a-zA-Z-][a-zA-Z0-9_-]*",
    a = [e.APOS_STRING_MODE, e.QUOTE_STRING_MODE];
  return {
    name: "CSS",
    case_insensitive: !0,
    illegal: /[=|'\$]/,
    keywords: { keyframePosition: "from to" },
    classNameAliases: { keyframePosition: "selector-tag" },
    contains: [
      n.BLOCK_COMMENT,
      r,
      n.CSS_NUMBER_MODE,
      { className: "selector-id", begin: /#[A-Za-z0-9_-]+/, relevance: 0 },
      { className: "selector-class", begin: "\\." + l, relevance: 0 },
      n.ATTRIBUTE_SELECTOR_MODE,
      {
        className: "selector-pseudo",
        variants: [
          { begin: ":(" + lC.join("|") + ")" },
          { begin: ":(:)?(" + aC.join("|") + ")" },
        ],
      },
      n.CSS_VARIABLE,
      { className: "attribute", begin: "\\b(" + sC.join("|") + ")\\b" },
      {
        begin: /:/,
        end: /[;}{]/,
        contains: [
          n.BLOCK_COMMENT,
          n.HEXCOLOR,
          n.IMPORTANT,
          n.CSS_NUMBER_MODE,
          ...a,
          {
            begin: /(url|data-uri)\(/,
            end: /\)/,
            relevance: 0,
            keywords: { built_in: "url data-uri" },
            contains: [
              ...a,
              {
                className: "string",
                begin: /[^)]/,
                endsWithParent: !0,
                excludeEnd: !0,
              },
            ],
          },
          n.FUNCTION_DISPATCH,
        ],
      },
      {
        begin: t.lookahead(/@/),
        end: "[{;]",
        relevance: 0,
        illegal: /:/,
        contains: [
          { className: "keyword", begin: o },
          {
            begin: /\s/,
            endsWithParent: !0,
            excludeEnd: !0,
            relevance: 0,
            keywords: {
              $pattern: /[a-z-]+/,
              keyword: i,
              attribute: oC.join(" "),
            },
            contains: [
              { begin: /[a-z-]+(?=:)/, className: "attribute" },
              ...a,
              n.CSS_NUMBER_MODE,
            ],
          },
        ],
      },
      { className: "selector-tag", begin: "\\b(" + iC.join("|") + ")\\b" },
    ],
  };
}
function cC(e) {
  const t = e.regex;
  return {
    name: "Diff",
    aliases: ["patch"],
    contains: [
      {
        className: "meta",
        relevance: 10,
        match: t.either(
          /^@@ +-\d+,\d+ +\+\d+,\d+ +@@/,
          /^\*\*\* +\d+,\d+ +\*\*\*\*$/,
          /^--- +\d+,\d+ +----$/,
        ),
      },
      {
        className: "comment",
        variants: [
          {
            begin: t.either(
              /Index: /,
              /^index/,
              /={3,}/,
              /^-{3}/,
              /^\*{3} /,
              /^\+{3}/,
              /^diff --git/,
            ),
            end: /$/,
          },
          { match: /^\*{15}$/ },
        ],
      },
      { className: "addition", begin: /^\+/, end: /$/ },
      { className: "deletion", begin: /^-/, end: /$/ },
      { className: "addition", begin: /^!/, end: /$/ },
    ],
  };
}
function dC(e) {
  const o = {
    keyword: [
      "break",
      "case",
      "chan",
      "const",
      "continue",
      "default",
      "defer",
      "else",
      "fallthrough",
      "for",
      "func",
      "go",
      "goto",
      "if",
      "import",
      "interface",
      "map",
      "package",
      "range",
      "return",
      "select",
      "struct",
      "switch",
      "type",
      "var",
    ],
    type: [
      "bool",
      "byte",
      "complex64",
      "complex128",
      "error",
      "float32",
      "float64",
      "int8",
      "int16",
      "int32",
      "int64",
      "string",
      "uint8",
      "uint16",
      "uint32",
      "uint64",
      "int",
      "uint",
      "uintptr",
      "rune",
    ],
    literal: ["true", "false", "iota", "nil"],
    built_in: [
      "append",
      "cap",
      "close",
      "complex",
      "copy",
      "imag",
      "len",
      "make",
      "new",
      "panic",
      "print",
      "println",
      "real",
      "recover",
      "delete",
    ],
  };
  return {
    name: "Go",
    aliases: ["golang"],
    keywords: o,
    illegal: "</",
    contains: [
      e.C_LINE_COMMENT_MODE,
      e.C_BLOCK_COMMENT_MODE,
      {
        className: "string",
        variants: [
          e.QUOTE_STRING_MODE,
          e.APOS_STRING_MODE,
          { begin: "`", end: "`" },
        ],
      },
      {
        className: "number",
        variants: [
          {
            match: /-?\b0[xX]\.[a-fA-F0-9](_?[a-fA-F0-9])*[pP][+-]?\d(_?\d)*i?/,
            relevance: 0,
          },
          {
            match:
              /-?\b0[xX](_?[a-fA-F0-9])+((\.([a-fA-F0-9](_?[a-fA-F0-9])*)?)?[pP][+-]?\d(_?\d)*)?i?/,
            relevance: 0,
          },
          { match: /-?\b0[oO](_?[0-7])*i?/, relevance: 0 },
          { match: /-?\.\d(_?\d)*([eE][+-]?\d(_?\d)*)?i?/, relevance: 0 },
          {
            match: /-?\b\d(_?\d)*(\.(\d(_?\d)*)?)?([eE][+-]?\d(_?\d)*)?i?/,
            relevance: 0,
          },
        ],
      },
      { begin: /:=/ },
      {
        className: "function",
        beginKeywords: "func",
        end: "\\s*(\\{|$)",
        excludeEnd: !0,
        contains: [
          e.TITLE_MODE,
          {
            className: "params",
            begin: /\(/,
            end: /\)/,
            endsParent: !0,
            keywords: o,
            illegal: /["']/,
          },
        ],
      },
    ],
  };
}
function fC(e) {
  const t = e.regex,
    n = /[_A-Za-z][_0-9A-Za-z]*/;
  return {
    name: "GraphQL",
    aliases: ["gql"],
    case_insensitive: !0,
    disableAutodetect: !1,
    keywords: {
      keyword: [
        "query",
        "mutation",
        "subscription",
        "type",
        "input",
        "schema",
        "directive",
        "interface",
        "union",
        "scalar",
        "fragment",
        "enum",
        "on",
      ],
      literal: ["true", "false", "null"],
    },
    contains: [
      e.HASH_COMMENT_MODE,
      e.QUOTE_STRING_MODE,
      e.NUMBER_MODE,
      { scope: "punctuation", match: /[.]{3}/, relevance: 0 },
      {
        scope: "punctuation",
        begin: /[\!\(\)\:\=\[\]\{\|\}]{1}/,
        relevance: 0,
      },
      {
        scope: "variable",
        begin: /\$/,
        end: /\W/,
        excludeEnd: !0,
        relevance: 0,
      },
      { scope: "meta", match: /@\w+/, excludeEnd: !0 },
      {
        scope: "symbol",
        begin: t.concat(n, t.lookahead(/\s*:/)),
        relevance: 0,
      },
    ],
    illegal: [/[;<']/, /BEGIN/],
  };
}
function pC(e) {
  const t = e.regex,
    n = {
      className: "number",
      relevance: 0,
      variants: [{ begin: /([+-]+)?[\d]+_[\d_]+/ }, { begin: e.NUMBER_RE }],
    },
    r = e.COMMENT();
  r.variants = [
    { begin: /;/, end: /$/ },
    { begin: /#/, end: /$/ },
  ];
  const i = {
      className: "variable",
      variants: [{ begin: /\$[\w\d"][\w\d_]*/ }, { begin: /\$\{(.*?)\}/ }],
    },
    o = { className: "literal", begin: /\bon|off|true|false|yes|no\b/ },
    l = {
      className: "string",
      contains: [e.BACKSLASH_ESCAPE],
      variants: [
        { begin: "'''", end: "'''", relevance: 10 },
        { begin: '"""', end: '"""', relevance: 10 },
        { begin: '"', end: '"' },
        { begin: "'", end: "'" },
      ],
    },
    a = {
      begin: /\[/,
      end: /\]/,
      contains: [r, o, i, l, n, "self"],
      relevance: 0,
    },
    s = /[A-Za-z0-9_-]+/,
    u = /"(\\"|[^"])*"/,
    d = /'[^']*'/,
    c = t.either(s, u, d),
    f = t.concat(c, "(\\s*\\.\\s*", c, ")*", t.lookahead(/\s*=\s*[^#\s]/));
  return {
    name: "TOML, also INI",
    aliases: ["toml"],
    case_insensitive: !0,
    illegal: /\S/,
    contains: [
      r,
      { className: "section", begin: /\[+/, end: /\]+/ },
      {
        begin: f,
        className: "attr",
        starts: { end: /$/, contains: [r, a, o, i, l, n] },
      },
    ],
  };
}
var cr = "[0-9](_*[0-9])*",
  Ro = `\\.(${cr})`,
  Oo = "[0-9a-fA-F](_*[0-9a-fA-F])*",
  Qf = {
    className: "number",
    variants: [
      { begin: `(\\b(${cr})((${Ro})|\\.)?|(${Ro}))[eE][+-]?(${cr})[fFdD]?\\b` },
      { begin: `\\b(${cr})((${Ro})[fFdD]?\\b|\\.([fFdD]\\b)?)` },
      { begin: `(${Ro})[fFdD]?\\b` },
      { begin: `\\b(${cr})[fFdD]\\b` },
      {
        begin: `\\b0[xX]((${Oo})\\.?|(${Oo})?\\.(${Oo}))[pP][+-]?(${cr})[fFdD]?\\b`,
      },
      { begin: "\\b(0|[1-9](_*[0-9])*)[lL]?\\b" },
      { begin: `\\b0[xX](${Oo})[lL]?\\b` },
      { begin: "\\b0(_*[0-7])*[lL]?\\b" },
      { begin: "\\b0[bB][01](_*[01])*[lL]?\\b" },
    ],
    relevance: 0,
  };
function ey(e, t, n) {
  return n === -1 ? "" : e.replace(t, (r) => ey(e, t, n - 1));
}
function hC(e) {
  const t = e.regex,
    n = "[À-ʸa-zA-Z_$][À-ʸa-zA-Z_$0-9]*",
    r = n + ey("(?:<" + n + "~~~(?:\\s*,\\s*" + n + "~~~)*>)?", /~~~/g, 2),
    s = {
      keyword: [
        "synchronized",
        "abstract",
        "private",
        "var",
        "static",
        "if",
        "const ",
        "for",
        "while",
        "strictfp",
        "finally",
        "protected",
        "import",
        "native",
        "final",
        "void",
        "enum",
        "else",
        "break",
        "transient",
        "catch",
        "instanceof",
        "volatile",
        "case",
        "assert",
        "package",
        "default",
        "public",
        "try",
        "switch",
        "continue",
        "throws",
        "protected",
        "public",
        "private",
        "module",
        "requires",
        "exports",
        "do",
        "sealed",
        "yield",
        "permits",
        "goto",
        "when",
      ],
      literal: ["false", "true", "null"],
      type: [
        "char",
        "boolean",
        "long",
        "float",
        "int",
        "byte",
        "short",
        "double",
      ],
      built_in: ["super", "this"],
    },
    u = {
      className: "meta",
      begin: "@" + n,
      contains: [{ begin: /\(/, end: /\)/, contains: ["self"] }],
    },
    d = {
      className: "params",
      begin: /\(/,
      end: /\)/,
      keywords: s,
      relevance: 0,
      contains: [e.C_BLOCK_COMMENT_MODE],
      endsParent: !0,
    };
  return {
    name: "Java",
    aliases: ["jsp"],
    keywords: s,
    illegal: /<\/|#/,
    contains: [
      e.COMMENT("/\\*\\*", "\\*/", {
        relevance: 0,
        contains: [
          { begin: /\w+@/, relevance: 0 },
          { className: "doctag", begin: "@[A-Za-z]+" },
        ],
      }),
      { begin: /import java\.[a-z]+\./, keywords: "import", relevance: 2 },
      e.C_LINE_COMMENT_MODE,
      e.C_BLOCK_COMMENT_MODE,
      {
        begin: /"""/,
        end: /"""/,
        className: "string",
        contains: [e.BACKSLASH_ESCAPE],
      },
      e.APOS_STRING_MODE,
      e.QUOTE_STRING_MODE,
      {
        match: [/\b(?:class|interface|enum|extends|implements|new)/, /\s+/, n],
        className: { 1: "keyword", 3: "title.class" },
      },
      { match: /non-sealed/, scope: "keyword" },
      {
        begin: [t.concat(/(?!else)/, n), /\s+/, n, /\s+/, /=(?!=)/],
        className: { 1: "type", 3: "variable", 5: "operator" },
      },
      {
        begin: [/record/, /\s+/, n],
        className: { 1: "keyword", 3: "title.class" },
        contains: [d, e.C_LINE_COMMENT_MODE, e.C_BLOCK_COMMENT_MODE],
      },
      { beginKeywords: "new throw return else", relevance: 0 },
      {
        begin: ["(?:" + r + "\\s+)", e.UNDERSCORE_IDENT_RE, /\s*(?=\()/],
        className: { 2: "title.function" },
        keywords: s,
        contains: [
          {
            className: "params",
            begin: /\(/,
            end: /\)/,
            keywords: s,
            relevance: 0,
            contains: [
              u,
              e.APOS_STRING_MODE,
              e.QUOTE_STRING_MODE,
              Qf,
              e.C_BLOCK_COMMENT_MODE,
            ],
          },
          e.C_LINE_COMMENT_MODE,
          e.C_BLOCK_COMMENT_MODE,
        ],
      },
      Qf,
      u,
    ],
  };
}
const Zf = "[A-Za-z$_][0-9A-Za-z$_]*",
  gC = [
    "as",
    "in",
    "of",
    "if",
    "for",
    "while",
    "finally",
    "var",
    "new",
    "function",
    "do",
    "return",
    "void",
    "else",
    "break",
    "catch",
    "instanceof",
    "with",
    "throw",
    "case",
    "default",
    "try",
    "switch",
    "continue",
    "typeof",
    "delete",
    "let",
    "yield",
    "const",
    "class",
    "debugger",
    "async",
    "await",
    "static",
    "import",
    "from",
    "export",
    "extends",
    "using",
  ],
  mC = ["true", "false", "null", "undefined", "NaN", "Infinity"],
  ty = [
    "Object",
    "Function",
    "Boolean",
    "Symbol",
    "Math",
    "Date",
    "Number",
    "BigInt",
    "String",
    "RegExp",
    "Array",
    "Float32Array",
    "Float64Array",
    "Int8Array",
    "Uint8Array",
    "Uint8ClampedArray",
    "Int16Array",
    "Int32Array",
    "Uint16Array",
    "Uint32Array",
    "BigInt64Array",
    "BigUint64Array",
    "Set",
    "Map",
    "WeakSet",
    "WeakMap",
    "ArrayBuffer",
    "SharedArrayBuffer",
    "Atomics",
    "DataView",
    "JSON",
    "Promise",
    "Generator",
    "GeneratorFunction",
    "AsyncFunction",
    "Reflect",
    "Proxy",
    "Intl",
    "WebAssembly",
  ],
  ny = [
    "Error",
    "EvalError",
    "InternalError",
    "RangeError",
    "ReferenceError",
    "SyntaxError",
    "TypeError",
    "URIError",
  ],
  ry = [
    "setInterval",
    "setTimeout",
    "clearInterval",
    "clearTimeout",
    "require",
    "exports",
    "eval",
    "isFinite",
    "isNaN",
    "parseFloat",
    "parseInt",
    "decodeURI",
    "decodeURIComponent",
    "encodeURI",
    "encodeURIComponent",
    "escape",
    "unescape",
  ],
  yC = [
    "arguments",
    "this",
    "super",
    "console",
    "window",
    "document",
    "localStorage",
    "sessionStorage",
    "module",
    "global",
  ],
  bC = [].concat(ry, ty, ny);
function vC(e) {
  const t = e.regex,
    n = (C, { after: M }) => {
      const v = "</" + C[0].slice(1);
      return C.input.indexOf(v, M) !== -1;
    },
    r = Zf,
    i = { begin: "<>", end: "</>" },
    o = /<[A-Za-z0-9\\._:-]+\s*\/>/,
    l = {
      begin: /<[A-Za-z0-9\\._:-]+/,
      end: /\/[A-Za-z0-9\\._:-]+>|\/>/,
      isTrulyOpeningTag: (C, M) => {
        const v = C[0].length + C.index,
          H = C.input[v];
        if (H === "<" || H === ",") {
          M.ignoreMatch();
          return;
        }
        H === ">" && (n(C, { after: v }) || M.ignoreMatch());
        let K;
        const w = C.input.substring(v);
        if ((K = w.match(/^\s*=/))) {
          M.ignoreMatch();
          return;
        }
        if ((K = w.match(/^\s+extends\s+/)) && K.index === 0) {
          M.ignoreMatch();
          return;
        }
      },
    },
    a = {
      $pattern: Zf,
      keyword: gC,
      literal: mC,
      built_in: bC,
      "variable.language": yC,
    },
    s = "[0-9](_?[0-9])*",
    u = `\\.(${s})`,
    d = "0|[1-9](_?[0-9])*|0[0-7]*[89][0-9]*",
    c = {
      className: "number",
      variants: [
        { begin: `(\\b(${d})((${u})|\\.)?|(${u}))[eE][+-]?(${s})\\b` },
        { begin: `\\b(${d})\\b((${u})\\b|\\.)?|(${u})\\b` },
        { begin: "\\b(0|[1-9](_?[0-9])*)n\\b" },
        { begin: "\\b0[xX][0-9a-fA-F](_?[0-9a-fA-F])*n?\\b" },
        { begin: "\\b0[bB][0-1](_?[0-1])*n?\\b" },
        { begin: "\\b0[oO][0-7](_?[0-7])*n?\\b" },
        { begin: "\\b0[0-7]+n?\\b" },
      ],
      relevance: 0,
    },
    f = {
      className: "subst",
      begin: "\\$\\{",
      end: "\\}",
      keywords: a,
      contains: [],
    },
    p = {
      begin: ".?html`",
      end: "",
      starts: {
        end: "`",
        returnEnd: !1,
        contains: [e.BACKSLASH_ESCAPE, f],
        subLanguage: "xml",
      },
    },
    g = {
      begin: ".?css`",
      end: "",
      starts: {
        end: "`",
        returnEnd: !1,
        contains: [e.BACKSLASH_ESCAPE, f],
        subLanguage: "css",
      },
    },
    y = {
      begin: ".?gql`",
      end: "",
      starts: {
        end: "`",
        returnEnd: !1,
        contains: [e.BACKSLASH_ESCAPE, f],
        subLanguage: "graphql",
      },
    },
    E = {
      className: "string",
      begin: "`",
      end: "`",
      contains: [e.BACKSLASH_ESCAPE, f],
    },
    m = {
      className: "comment",
      variants: [
        e.COMMENT(/\/\*\*(?!\/)/, "\\*/", {
          relevance: 0,
          contains: [
            {
              begin: "(?=@[A-Za-z]+)",
              relevance: 0,
              contains: [
                { className: "doctag", begin: "@[A-Za-z]+" },
                {
                  className: "type",
                  begin: "\\{",
                  end: "\\}",
                  excludeEnd: !0,
                  excludeBegin: !0,
                  relevance: 0,
                },
                {
                  className: "variable",
                  begin: r + "(?=\\s*(-)|$)",
                  endsParent: !0,
                  relevance: 0,
                },
                { begin: /(?=[^\n])\s/, relevance: 0 },
              ],
            },
          ],
        }),
        e.C_BLOCK_COMMENT_MODE,
        e.C_LINE_COMMENT_MODE,
      ],
    },
    b = [
      e.APOS_STRING_MODE,
      e.QUOTE_STRING_MODE,
      p,
      g,
      y,
      E,
      { match: /\$\d+/ },
      c,
    ];
  f.contains = b.concat({
    begin: /\{/,
    end: /\}/,
    keywords: a,
    contains: ["self"].concat(b),
  });
  const _ = [].concat(m, f.contains),
    N = _.concat([
      {
        begin: /(\s*)\(/,
        end: /\)/,
        keywords: a,
        contains: ["self"].concat(_),
      },
    ]),
    x = {
      className: "params",
      begin: /(\s*)\(/,
      end: /\)/,
      excludeBegin: !0,
      excludeEnd: !0,
      keywords: a,
      contains: N,
    },
    O = {
      variants: [
        {
          match: [
            /class/,
            /\s+/,
            r,
            /\s+/,
            /extends/,
            /\s+/,
            t.concat(r, "(", t.concat(/\./, r), ")*"),
          ],
          scope: {
            1: "keyword",
            3: "title.class",
            5: "keyword",
            7: "title.class.inherited",
          },
        },
        {
          match: [/class/, /\s+/, r],
          scope: { 1: "keyword", 3: "title.class" },
        },
      ],
    },
    I = {
      relevance: 0,
      match: t.either(
        /\bJSON/,
        /\b[A-Z][a-z]+([A-Z][a-z]*|\d)*/,
        /\b[A-Z]{2,}([A-Z][a-z]+|\d)+([A-Z][a-z]*)*/,
        /\b[A-Z]{2,}[a-z]+([A-Z][a-z]+|\d)*([A-Z][a-z]*)*/,
      ),
      className: "title.class",
      keywords: { _: [...ty, ...ny] },
    },
    U = {
      label: "use_strict",
      className: "meta",
      relevance: 10,
      begin: /^\s*['"]use (strict|asm)['"]/,
    },
    S = {
      variants: [
        { match: [/function/, /\s+/, r, /(?=\s*\()/] },
        { match: [/function/, /\s*(?=\()/] },
      ],
      className: { 1: "keyword", 3: "title.function" },
      label: "func.def",
      contains: [x],
      illegal: /%/,
    },
    F = {
      relevance: 0,
      match: /\b[A-Z][A-Z_0-9]+\b/,
      className: "variable.constant",
    };
  function L(C) {
    return t.concat("(?!", C.join("|"), ")");
  }
  const Q = {
      match: t.concat(
        /\b/,
        L([...ry, "super", "import"].map((C) => `${C}\\s*\\(`)),
        r,
        t.lookahead(/\s*\(/),
      ),
      className: "title.function",
      relevance: 0,
    },
    V = {
      begin: t.concat(/\./, t.lookahead(t.concat(r, /(?![0-9A-Za-z$_(])/))),
      end: r,
      excludeBegin: !0,
      keywords: "prototype",
      className: "property",
      relevance: 0,
    },
    G = {
      match: [/get|set/, /\s+/, r, /(?=\()/],
      className: { 1: "keyword", 3: "title.function" },
      contains: [{ begin: /\(\)/ }, x],
    },
    R =
      "(\\([^()]*(\\([^()]*(\\([^()]*\\)[^()]*)*\\)[^()]*)*\\)|" +
      e.UNDERSCORE_IDENT_RE +
      ")\\s*=>",
    B = {
      match: [
        /const|var|let/,
        /\s+/,
        r,
        /\s*/,
        /=\s*/,
        /(async\s*)?/,
        t.lookahead(R),
      ],
      keywords: "async",
      className: { 1: "keyword", 3: "title.function" },
      contains: [x],
    };
  return {
    name: "JavaScript",
    aliases: ["js", "jsx", "mjs", "cjs"],
    keywords: a,
    exports: { PARAMS_CONTAINS: N, CLASS_REFERENCE: I },
    illegal: /#(?![$_A-z])/,
    contains: [
      e.SHEBANG({ label: "shebang", binary: "node", relevance: 5 }),
      U,
      e.APOS_STRING_MODE,
      e.QUOTE_STRING_MODE,
      p,
      g,
      y,
      E,
      m,
      { match: /\$\d+/ },
      c,
      I,
      { scope: "attr", match: r + t.lookahead(":"), relevance: 0 },
      B,
      {
        begin: "(" + e.RE_STARTERS_RE + "|\\b(case|return|throw)\\b)\\s*",
        keywords: "return throw case",
        relevance: 0,
        contains: [
          m,
          e.REGEXP_MODE,
          {
            className: "function",
            begin: R,
            returnBegin: !0,
            end: "\\s*=>",
            contains: [
              {
                className: "params",
                variants: [
                  { begin: e.UNDERSCORE_IDENT_RE, relevance: 0 },
                  { className: null, begin: /\(\s*\)/, skip: !0 },
                  {
                    begin: /(\s*)\(/,
                    end: /\)/,
                    excludeBegin: !0,
                    excludeEnd: !0,
                    keywords: a,
                    contains: N,
                  },
                ],
              },
            ],
          },
          { begin: /,/, relevance: 0 },
          { match: /\s+/, relevance: 0 },
          {
            variants: [
              { begin: i.begin, end: i.end },
              { match: o },
              { begin: l.begin, "on:begin": l.isTrulyOpeningTag, end: l.end },
            ],
            subLanguage: "xml",
            contains: [
              { begin: l.begin, end: l.end, skip: !0, contains: ["self"] },
            ],
          },
        ],
      },
      S,
      { beginKeywords: "while if switch catch for" },
      {
        begin:
          "\\b(?!function)" +
          e.UNDERSCORE_IDENT_RE +
          "\\([^()]*(\\([^()]*(\\([^()]*\\)[^()]*)*\\)[^()]*)*\\)\\s*\\{",
        returnBegin: !0,
        label: "func.def",
        contains: [
          x,
          e.inherit(e.TITLE_MODE, { begin: r, className: "title.function" }),
        ],
      },
      { match: /\.\.\./, relevance: 0 },
      V,
      { match: "\\$" + r, relevance: 0 },
      {
        match: [/\bconstructor(?=\s*\()/],
        className: { 1: "title.function" },
        contains: [x],
      },
      Q,
      F,
      O,
      G,
      { match: /\$[(.]/ },
    ],
  };
}
function EC(e) {
  const t = {
      className: "attr",
      begin: /"(\\.|[^\\"\r\n])*"(?=\s*:)/,
      relevance: 1.01,
    },
    n = { match: /[{}[\],:]/, className: "punctuation", relevance: 0 },
    r = ["true", "false", "null"],
    i = { scope: "literal", beginKeywords: r.join(" ") };
  return {
    name: "JSON",
    aliases: ["jsonc"],
    keywords: { literal: r },
    contains: [
      t,
      n,
      e.QUOTE_STRING_MODE,
      i,
      e.C_NUMBER_MODE,
      e.C_LINE_COMMENT_MODE,
      e.C_BLOCK_COMMENT_MODE,
    ],
    illegal: "\\S",
  };
}
var dr = "[0-9](_*[0-9])*",
  Io = `\\.(${dr})`,
  Mo = "[0-9a-fA-F](_*[0-9a-fA-F])*",
  wC = {
    className: "number",
    variants: [
      { begin: `(\\b(${dr})((${Io})|\\.)?|(${Io}))[eE][+-]?(${dr})[fFdD]?\\b` },
      { begin: `\\b(${dr})((${Io})[fFdD]?\\b|\\.([fFdD]\\b)?)` },
      { begin: `(${Io})[fFdD]?\\b` },
      { begin: `\\b(${dr})[fFdD]\\b` },
      {
        begin: `\\b0[xX]((${Mo})\\.?|(${Mo})?\\.(${Mo}))[pP][+-]?(${dr})[fFdD]?\\b`,
      },
      { begin: "\\b(0|[1-9](_*[0-9])*)[lL]?\\b" },
      { begin: `\\b0[xX](${Mo})[lL]?\\b` },
      { begin: "\\b0(_*[0-7])*[lL]?\\b" },
      { begin: "\\b0[bB][01](_*[01])*[lL]?\\b" },
    ],
    relevance: 0,
  };
function xC(e) {
  const t = {
      keyword:
        "abstract as val var vararg get set class object open private protected public noinline crossinline dynamic final enum if else do while for when throw try catch finally import package is in fun override companion reified inline lateinit init interface annotation data sealed internal infix operator out by constructor super tailrec where const inner suspend typealias external expect actual",
      built_in:
        "Byte Short Char Int Long Boolean Float Double Void Unit Nothing",
      literal: "true false null",
    },
    n = {
      className: "keyword",
      begin: /\b(break|continue|return|this)\b/,
      starts: { contains: [{ className: "symbol", begin: /@\w+/ }] },
    },
    r = { className: "symbol", begin: e.UNDERSCORE_IDENT_RE + "@" },
    i = {
      className: "subst",
      begin: /\$\{/,
      end: /\}/,
      contains: [e.C_NUMBER_MODE],
    },
    o = { className: "variable", begin: "\\$" + e.UNDERSCORE_IDENT_RE },
    l = {
      className: "string",
      variants: [
        { begin: '"""', end: '"""(?=[^"])', contains: [o, i] },
        { begin: "'", end: "'", illegal: /\n/, contains: [e.BACKSLASH_ESCAPE] },
        {
          begin: '"',
          end: '"',
          illegal: /\n/,
          contains: [e.BACKSLASH_ESCAPE, o, i],
        },
      ],
    };
  i.contains.push(l);
  const a = {
      className: "meta",
      begin:
        "@(?:file|property|field|get|set|receiver|param|setparam|delegate)\\s*:(?:\\s*" +
        e.UNDERSCORE_IDENT_RE +
        ")?",
    },
    s = {
      className: "meta",
      begin: "@" + e.UNDERSCORE_IDENT_RE,
      contains: [
        {
          begin: /\(/,
          end: /\)/,
          contains: [e.inherit(l, { className: "string" }), "self"],
        },
      ],
    },
    u = wC,
    d = e.COMMENT("/\\*", "\\*/", { contains: [e.C_BLOCK_COMMENT_MODE] }),
    c = {
      variants: [
        { className: "type", begin: e.UNDERSCORE_IDENT_RE },
        { begin: /\(/, end: /\)/, contains: [] },
      ],
    },
    f = c;
  return (
    (f.variants[1].contains = [c]),
    (c.variants[1].contains = [f]),
    {
      name: "Kotlin",
      aliases: ["kt", "kts"],
      keywords: t,
      contains: [
        e.COMMENT("/\\*\\*", "\\*/", {
          relevance: 0,
          contains: [{ className: "doctag", begin: "@[A-Za-z]+" }],
        }),
        e.C_LINE_COMMENT_MODE,
        d,
        n,
        r,
        a,
        s,
        {
          className: "function",
          beginKeywords: "fun",
          end: "[(]|$",
          returnBegin: !0,
          excludeEnd: !0,
          keywords: t,
          relevance: 5,
          contains: [
            {
              begin: e.UNDERSCORE_IDENT_RE + "\\s*\\(",
              returnBegin: !0,
              relevance: 0,
              contains: [e.UNDERSCORE_TITLE_MODE],
            },
            {
              className: "type",
              begin: /</,
              end: />/,
              keywords: "reified",
              relevance: 0,
            },
            {
              className: "params",
              begin: /\(/,
              end: /\)/,
              endsParent: !0,
              keywords: t,
              relevance: 0,
              contains: [
                {
                  begin: /:/,
                  end: /[=,\/]/,
                  endsWithParent: !0,
                  contains: [c, e.C_LINE_COMMENT_MODE, d],
                  relevance: 0,
                },
                e.C_LINE_COMMENT_MODE,
                d,
                a,
                s,
                l,
                e.C_NUMBER_MODE,
              ],
            },
            d,
          ],
        },
        {
          begin: [/class|interface|trait/, /\s+/, e.UNDERSCORE_IDENT_RE],
          beginScope: { 3: "title.class" },
          keywords: "class interface trait",
          end: /[:\{(]|$/,
          excludeEnd: !0,
          illegal: "extends implements",
          contains: [
            { beginKeywords: "public protected internal private constructor" },
            e.UNDERSCORE_TITLE_MODE,
            {
              className: "type",
              begin: /</,
              end: />/,
              excludeBegin: !0,
              excludeEnd: !0,
              relevance: 0,
            },
            {
              className: "type",
              begin: /[,:]\s*/,
              end: /[<\(,){\s]|$/,
              excludeBegin: !0,
              returnEnd: !0,
            },
            a,
            s,
          ],
        },
        l,
        {
          className: "meta",
          begin: "^#!/usr/bin/env",
          end: "$",
          illegal: `
`,
        },
        u,
      ],
    }
  );
}
const _C = (e) => ({
    IMPORTANT: { scope: "meta", begin: "!important" },
    BLOCK_COMMENT: e.C_BLOCK_COMMENT_MODE,
    HEXCOLOR: {
      scope: "number",
      begin: /#(([0-9a-fA-F]{3,4})|(([0-9a-fA-F]{2}){3,4}))\b/,
    },
    FUNCTION_DISPATCH: { className: "built_in", begin: /[\w-]+(?=\()/ },
    ATTRIBUTE_SELECTOR_MODE: {
      scope: "selector-attr",
      begin: /\[/,
      end: /\]/,
      illegal: "$",
      contains: [e.APOS_STRING_MODE, e.QUOTE_STRING_MODE],
    },
    CSS_NUMBER_MODE: {
      scope: "number",
      begin:
        e.NUMBER_RE +
        "(%|em|ex|ch|rem|vw|vh|vmin|vmax|cm|mm|in|pt|pc|px|deg|grad|rad|turn|s|ms|Hz|kHz|dpi|dpcm|dppx)?",
      relevance: 0,
    },
    CSS_VARIABLE: { className: "attr", begin: /--[A-Za-z_][A-Za-z0-9_-]*/ },
  }),
  kC = [
    "a",
    "abbr",
    "address",
    "article",
    "aside",
    "audio",
    "b",
    "blockquote",
    "body",
    "button",
    "canvas",
    "caption",
    "cite",
    "code",
    "dd",
    "del",
    "details",
    "dfn",
    "div",
    "dl",
    "dt",
    "em",
    "fieldset",
    "figcaption",
    "figure",
    "footer",
    "form",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "header",
    "hgroup",
    "html",
    "i",
    "iframe",
    "img",
    "input",
    "ins",
    "kbd",
    "label",
    "legend",
    "li",
    "main",
    "mark",
    "menu",
    "nav",
    "object",
    "ol",
    "optgroup",
    "option",
    "p",
    "picture",
    "q",
    "quote",
    "samp",
    "section",
    "select",
    "source",
    "span",
    "strong",
    "summary",
    "sup",
    "table",
    "tbody",
    "td",
    "textarea",
    "tfoot",
    "th",
    "thead",
    "time",
    "tr",
    "ul",
    "var",
    "video",
  ],
  SC = [
    "defs",
    "g",
    "marker",
    "mask",
    "pattern",
    "svg",
    "switch",
    "symbol",
    "feBlend",
    "feColorMatrix",
    "feComponentTransfer",
    "feComposite",
    "feConvolveMatrix",
    "feDiffuseLighting",
    "feDisplacementMap",
    "feFlood",
    "feGaussianBlur",
    "feImage",
    "feMerge",
    "feMorphology",
    "feOffset",
    "feSpecularLighting",
    "feTile",
    "feTurbulence",
    "linearGradient",
    "radialGradient",
    "stop",
    "circle",
    "ellipse",
    "image",
    "line",
    "path",
    "polygon",
    "polyline",
    "rect",
    "text",
    "use",
    "textPath",
    "tspan",
    "foreignObject",
    "clipPath",
  ],
  NC = [...kC, ...SC],
  CC = [
    "any-hover",
    "any-pointer",
    "aspect-ratio",
    "color",
    "color-gamut",
    "color-index",
    "device-aspect-ratio",
    "device-height",
    "device-width",
    "display-mode",
    "forced-colors",
    "grid",
    "height",
    "hover",
    "inverted-colors",
    "monochrome",
    "orientation",
    "overflow-block",
    "overflow-inline",
    "pointer",
    "prefers-color-scheme",
    "prefers-contrast",
    "prefers-reduced-motion",
    "prefers-reduced-transparency",
    "resolution",
    "scan",
    "scripting",
    "update",
    "width",
    "min-width",
    "max-width",
    "min-height",
    "max-height",
  ]
    .sort()
    .reverse(),
  iy = [
    "active",
    "any-link",
    "blank",
    "checked",
    "current",
    "default",
    "defined",
    "dir",
    "disabled",
    "drop",
    "empty",
    "enabled",
    "first",
    "first-child",
    "first-of-type",
    "fullscreen",
    "future",
    "focus",
    "focus-visible",
    "focus-within",
    "has",
    "host",
    "host-context",
    "hover",
    "indeterminate",
    "in-range",
    "invalid",
    "is",
    "lang",
    "last-child",
    "last-of-type",
    "left",
    "link",
    "local-link",
    "not",
    "nth-child",
    "nth-col",
    "nth-last-child",
    "nth-last-col",
    "nth-last-of-type",
    "nth-of-type",
    "only-child",
    "only-of-type",
    "optional",
    "out-of-range",
    "past",
    "placeholder-shown",
    "read-only",
    "read-write",
    "required",
    "right",
    "root",
    "scope",
    "target",
    "target-within",
    "user-invalid",
    "valid",
    "visited",
    "where",
  ]
    .sort()
    .reverse(),
  oy = [
    "after",
    "backdrop",
    "before",
    "cue",
    "cue-region",
    "first-letter",
    "first-line",
    "grammar-error",
    "marker",
    "part",
    "placeholder",
    "selection",
    "slotted",
    "spelling-error",
  ]
    .sort()
    .reverse(),
  TC = [
    "accent-color",
    "align-content",
    "align-items",
    "align-self",
    "alignment-baseline",
    "all",
    "anchor-name",
    "animation",
    "animation-composition",
    "animation-delay",
    "animation-direction",
    "animation-duration",
    "animation-fill-mode",
    "animation-iteration-count",
    "animation-name",
    "animation-play-state",
    "animation-range",
    "animation-range-end",
    "animation-range-start",
    "animation-timeline",
    "animation-timing-function",
    "appearance",
    "aspect-ratio",
    "backdrop-filter",
    "backface-visibility",
    "background",
    "background-attachment",
    "background-blend-mode",
    "background-clip",
    "background-color",
    "background-image",
    "background-origin",
    "background-position",
    "background-position-x",
    "background-position-y",
    "background-repeat",
    "background-size",
    "baseline-shift",
    "block-size",
    "border",
    "border-block",
    "border-block-color",
    "border-block-end",
    "border-block-end-color",
    "border-block-end-style",
    "border-block-end-width",
    "border-block-start",
    "border-block-start-color",
    "border-block-start-style",
    "border-block-start-width",
    "border-block-style",
    "border-block-width",
    "border-bottom",
    "border-bottom-color",
    "border-bottom-left-radius",
    "border-bottom-right-radius",
    "border-bottom-style",
    "border-bottom-width",
    "border-collapse",
    "border-color",
    "border-end-end-radius",
    "border-end-start-radius",
    "border-image",
    "border-image-outset",
    "border-image-repeat",
    "border-image-slice",
    "border-image-source",
    "border-image-width",
    "border-inline",
    "border-inline-color",
    "border-inline-end",
    "border-inline-end-color",
    "border-inline-end-style",
    "border-inline-end-width",
    "border-inline-start",
    "border-inline-start-color",
    "border-inline-start-style",
    "border-inline-start-width",
    "border-inline-style",
    "border-inline-width",
    "border-left",
    "border-left-color",
    "border-left-style",
    "border-left-width",
    "border-radius",
    "border-right",
    "border-right-color",
    "border-right-style",
    "border-right-width",
    "border-spacing",
    "border-start-end-radius",
    "border-start-start-radius",
    "border-style",
    "border-top",
    "border-top-color",
    "border-top-left-radius",
    "border-top-right-radius",
    "border-top-style",
    "border-top-width",
    "border-width",
    "bottom",
    "box-align",
    "box-decoration-break",
    "box-direction",
    "box-flex",
    "box-flex-group",
    "box-lines",
    "box-ordinal-group",
    "box-orient",
    "box-pack",
    "box-shadow",
    "box-sizing",
    "break-after",
    "break-before",
    "break-inside",
    "caption-side",
    "caret-color",
    "clear",
    "clip",
    "clip-path",
    "clip-rule",
    "color",
    "color-interpolation",
    "color-interpolation-filters",
    "color-profile",
    "color-rendering",
    "color-scheme",
    "column-count",
    "column-fill",
    "column-gap",
    "column-rule",
    "column-rule-color",
    "column-rule-style",
    "column-rule-width",
    "column-span",
    "column-width",
    "columns",
    "contain",
    "contain-intrinsic-block-size",
    "contain-intrinsic-height",
    "contain-intrinsic-inline-size",
    "contain-intrinsic-size",
    "contain-intrinsic-width",
    "container",
    "container-name",
    "container-type",
    "content",
    "content-visibility",
    "counter-increment",
    "counter-reset",
    "counter-set",
    "cue",
    "cue-after",
    "cue-before",
    "cursor",
    "cx",
    "cy",
    "direction",
    "display",
    "dominant-baseline",
    "empty-cells",
    "enable-background",
    "field-sizing",
    "fill",
    "fill-opacity",
    "fill-rule",
    "filter",
    "flex",
    "flex-basis",
    "flex-direction",
    "flex-flow",
    "flex-grow",
    "flex-shrink",
    "flex-wrap",
    "float",
    "flood-color",
    "flood-opacity",
    "flow",
    "font",
    "font-display",
    "font-family",
    "font-feature-settings",
    "font-kerning",
    "font-language-override",
    "font-optical-sizing",
    "font-palette",
    "font-size",
    "font-size-adjust",
    "font-smooth",
    "font-smoothing",
    "font-stretch",
    "font-style",
    "font-synthesis",
    "font-synthesis-position",
    "font-synthesis-small-caps",
    "font-synthesis-style",
    "font-synthesis-weight",
    "font-variant",
    "font-variant-alternates",
    "font-variant-caps",
    "font-variant-east-asian",
    "font-variant-emoji",
    "font-variant-ligatures",
    "font-variant-numeric",
    "font-variant-position",
    "font-variation-settings",
    "font-weight",
    "forced-color-adjust",
    "gap",
    "glyph-orientation-horizontal",
    "glyph-orientation-vertical",
    "grid",
    "grid-area",
    "grid-auto-columns",
    "grid-auto-flow",
    "grid-auto-rows",
    "grid-column",
    "grid-column-end",
    "grid-column-start",
    "grid-gap",
    "grid-row",
    "grid-row-end",
    "grid-row-start",
    "grid-template",
    "grid-template-areas",
    "grid-template-columns",
    "grid-template-rows",
    "hanging-punctuation",
    "height",
    "hyphenate-character",
    "hyphenate-limit-chars",
    "hyphens",
    "icon",
    "image-orientation",
    "image-rendering",
    "image-resolution",
    "ime-mode",
    "initial-letter",
    "initial-letter-align",
    "inline-size",
    "inset",
    "inset-area",
    "inset-block",
    "inset-block-end",
    "inset-block-start",
    "inset-inline",
    "inset-inline-end",
    "inset-inline-start",
    "isolation",
    "justify-content",
    "justify-items",
    "justify-self",
    "kerning",
    "left",
    "letter-spacing",
    "lighting-color",
    "line-break",
    "line-height",
    "line-height-step",
    "list-style",
    "list-style-image",
    "list-style-position",
    "list-style-type",
    "margin",
    "margin-block",
    "margin-block-end",
    "margin-block-start",
    "margin-bottom",
    "margin-inline",
    "margin-inline-end",
    "margin-inline-start",
    "margin-left",
    "margin-right",
    "margin-top",
    "margin-trim",
    "marker",
    "marker-end",
    "marker-mid",
    "marker-start",
    "marks",
    "mask",
    "mask-border",
    "mask-border-mode",
    "mask-border-outset",
    "mask-border-repeat",
    "mask-border-slice",
    "mask-border-source",
    "mask-border-width",
    "mask-clip",
    "mask-composite",
    "mask-image",
    "mask-mode",
    "mask-origin",
    "mask-position",
    "mask-repeat",
    "mask-size",
    "mask-type",
    "masonry-auto-flow",
    "math-depth",
    "math-shift",
    "math-style",
    "max-block-size",
    "max-height",
    "max-inline-size",
    "max-width",
    "min-block-size",
    "min-height",
    "min-inline-size",
    "min-width",
    "mix-blend-mode",
    "nav-down",
    "nav-index",
    "nav-left",
    "nav-right",
    "nav-up",
    "none",
    "normal",
    "object-fit",
    "object-position",
    "offset",
    "offset-anchor",
    "offset-distance",
    "offset-path",
    "offset-position",
    "offset-rotate",
    "opacity",
    "order",
    "orphans",
    "outline",
    "outline-color",
    "outline-offset",
    "outline-style",
    "outline-width",
    "overflow",
    "overflow-anchor",
    "overflow-block",
    "overflow-clip-margin",
    "overflow-inline",
    "overflow-wrap",
    "overflow-x",
    "overflow-y",
    "overlay",
    "overscroll-behavior",
    "overscroll-behavior-block",
    "overscroll-behavior-inline",
    "overscroll-behavior-x",
    "overscroll-behavior-y",
    "padding",
    "padding-block",
    "padding-block-end",
    "padding-block-start",
    "padding-bottom",
    "padding-inline",
    "padding-inline-end",
    "padding-inline-start",
    "padding-left",
    "padding-right",
    "padding-top",
    "page",
    "page-break-after",
    "page-break-before",
    "page-break-inside",
    "paint-order",
    "pause",
    "pause-after",
    "pause-before",
    "perspective",
    "perspective-origin",
    "place-content",
    "place-items",
    "place-self",
    "pointer-events",
    "position",
    "position-anchor",
    "position-visibility",
    "print-color-adjust",
    "quotes",
    "r",
    "resize",
    "rest",
    "rest-after",
    "rest-before",
    "right",
    "rotate",
    "row-gap",
    "ruby-align",
    "ruby-position",
    "scale",
    "scroll-behavior",
    "scroll-margin",
    "scroll-margin-block",
    "scroll-margin-block-end",
    "scroll-margin-block-start",
    "scroll-margin-bottom",
    "scroll-margin-inline",
    "scroll-margin-inline-end",
    "scroll-margin-inline-start",
    "scroll-margin-left",
    "scroll-margin-right",
    "scroll-margin-top",
    "scroll-padding",
    "scroll-padding-block",
    "scroll-padding-block-end",
    "scroll-padding-block-start",
    "scroll-padding-bottom",
    "scroll-padding-inline",
    "scroll-padding-inline-end",
    "scroll-padding-inline-start",
    "scroll-padding-left",
    "scroll-padding-right",
    "scroll-padding-top",
    "scroll-snap-align",
    "scroll-snap-stop",
    "scroll-snap-type",
    "scroll-timeline",
    "scroll-timeline-axis",
    "scroll-timeline-name",
    "scrollbar-color",
    "scrollbar-gutter",
    "scrollbar-width",
    "shape-image-threshold",
    "shape-margin",
    "shape-outside",
    "shape-rendering",
    "speak",
    "speak-as",
    "src",
    "stop-color",
    "stop-opacity",
    "stroke",
    "stroke-dasharray",
    "stroke-dashoffset",
    "stroke-linecap",
    "stroke-linejoin",
    "stroke-miterlimit",
    "stroke-opacity",
    "stroke-width",
    "tab-size",
    "table-layout",
    "text-align",
    "text-align-all",
    "text-align-last",
    "text-anchor",
    "text-combine-upright",
    "text-decoration",
    "text-decoration-color",
    "text-decoration-line",
    "text-decoration-skip",
    "text-decoration-skip-ink",
    "text-decoration-style",
    "text-decoration-thickness",
    "text-emphasis",
    "text-emphasis-color",
    "text-emphasis-position",
    "text-emphasis-style",
    "text-indent",
    "text-justify",
    "text-orientation",
    "text-overflow",
    "text-rendering",
    "text-shadow",
    "text-size-adjust",
    "text-transform",
    "text-underline-offset",
    "text-underline-position",
    "text-wrap",
    "text-wrap-mode",
    "text-wrap-style",
    "timeline-scope",
    "top",
    "touch-action",
    "transform",
    "transform-box",
    "transform-origin",
    "transform-style",
    "transition",
    "transition-behavior",
    "transition-delay",
    "transition-duration",
    "transition-property",
    "transition-timing-function",
    "translate",
    "unicode-bidi",
    "user-modify",
    "user-select",
    "vector-effect",
    "vertical-align",
    "view-timeline",
    "view-timeline-axis",
    "view-timeline-inset",
    "view-timeline-name",
    "view-transition-name",
    "visibility",
    "voice-balance",
    "voice-duration",
    "voice-family",
    "voice-pitch",
    "voice-range",
    "voice-rate",
    "voice-stress",
    "voice-volume",
    "white-space",
    "white-space-collapse",
    "widows",
    "width",
    "will-change",
    "word-break",
    "word-spacing",
    "word-wrap",
    "writing-mode",
    "x",
    "y",
    "z-index",
    "zoom",
  ]
    .sort()
    .reverse(),
  AC = iy.concat(oy).sort().reverse();
function RC(e) {
  const t = _C(e),
    n = AC,
    r = "and or not only",
    i = "[\\w-]+",
    o = "(" + i + "|@\\{" + i + "\\})",
    l = [],
    a = [],
    s = function (b) {
      return { className: "string", begin: "~?" + b + ".*?" + b };
    },
    u = function (b, _, N) {
      return { className: b, begin: _, relevance: N };
    },
    d = { $pattern: /[a-z-]+/, keyword: r, attribute: CC.join(" ") },
    c = { begin: "\\(", end: "\\)", contains: a, keywords: d, relevance: 0 };
  a.push(
    e.C_LINE_COMMENT_MODE,
    e.C_BLOCK_COMMENT_MODE,
    s("'"),
    s('"'),
    t.CSS_NUMBER_MODE,
    {
      begin: "(url|data-uri)\\(",
      starts: { className: "string", end: "[\\)\\n]", excludeEnd: !0 },
    },
    t.HEXCOLOR,
    c,
    u("variable", "@@?" + i, 10),
    u("variable", "@\\{" + i + "\\}"),
    u("built_in", "~?`[^`]*?`"),
    {
      className: "attribute",
      begin: i + "\\s*:",
      end: ":",
      returnBegin: !0,
      excludeEnd: !0,
    },
    t.IMPORTANT,
    { beginKeywords: "and not" },
    t.FUNCTION_DISPATCH,
  );
  const f = a.concat({ begin: /\{/, end: /\}/, contains: l }),
    p = {
      beginKeywords: "when",
      endsWithParent: !0,
      contains: [{ beginKeywords: "and not" }].concat(a),
    },
    g = {
      begin: o + "\\s*:",
      returnBegin: !0,
      end: /[;}]/,
      relevance: 0,
      contains: [
        { begin: /-(webkit|moz|ms|o)-/ },
        t.CSS_VARIABLE,
        {
          className: "attribute",
          begin: "\\b(" + TC.join("|") + ")\\b",
          end: /(?=:)/,
          starts: {
            endsWithParent: !0,
            illegal: "[<=$]",
            relevance: 0,
            contains: a,
          },
        },
      ],
    },
    y = {
      className: "keyword",
      begin:
        "@(import|media|charset|font-face|(-[a-z]+-)?keyframes|supports|document|namespace|page|viewport|host)\\b",
      starts: {
        end: "[;{}]",
        keywords: d,
        returnEnd: !0,
        contains: a,
        relevance: 0,
      },
    },
    E = {
      className: "variable",
      variants: [
        { begin: "@" + i + "\\s*:", relevance: 15 },
        { begin: "@" + i },
      ],
      starts: { end: "[;}]", returnEnd: !0, contains: f },
    },
    h = {
      variants: [
        { begin: "[\\.#:&\\[>]", end: "[;{}]" },
        { begin: o, end: /\{/ },
      ],
      returnBegin: !0,
      returnEnd: !0,
      illegal: `[<='$"]`,
      relevance: 0,
      contains: [
        e.C_LINE_COMMENT_MODE,
        e.C_BLOCK_COMMENT_MODE,
        p,
        u("keyword", "all\\b"),
        u("variable", "@\\{" + i + "\\}"),
        { begin: "\\b(" + NC.join("|") + ")\\b", className: "selector-tag" },
        t.CSS_NUMBER_MODE,
        u("selector-tag", o, 0),
        u("selector-id", "#" + o),
        u("selector-class", "\\." + o, 0),
        u("selector-tag", "&", 0),
        t.ATTRIBUTE_SELECTOR_MODE,
        { className: "selector-pseudo", begin: ":(" + iy.join("|") + ")" },
        { className: "selector-pseudo", begin: ":(:)?(" + oy.join("|") + ")" },
        { begin: /\(/, end: /\)/, relevance: 0, contains: f },
        { begin: "!important" },
        t.FUNCTION_DISPATCH,
      ],
    },
    m = { begin: i + `:(:)?(${n.join("|")})`, returnBegin: !0, contains: [h] };
  return (
    l.push(
      e.C_LINE_COMMENT_MODE,
      e.C_BLOCK_COMMENT_MODE,
      y,
      E,
      m,
      g,
      h,
      p,
      t.FUNCTION_DISPATCH,
    ),
    { name: "Less", case_insensitive: !0, illegal: `[=>'/<($"]`, contains: l }
  );
}
function OC(e) {
  const t = "\\[=*\\[",
    n = "\\]=*\\]",
    r = { begin: t, end: n, contains: ["self"] },
    i = [
      e.COMMENT("--(?!" + t + ")", "$"),
      e.COMMENT("--" + t, n, { contains: [r], relevance: 10 }),
    ];
  return {
    name: "Lua",
    aliases: ["pluto"],
    keywords: {
      $pattern: e.UNDERSCORE_IDENT_RE,
      literal: "true false nil",
      keyword:
        "and break do else elseif end for goto if in local not or repeat return then until while",
      built_in:
        "_G _ENV _VERSION __index __newindex __mode __call __metatable __tostring __len __gc __add __sub __mul __div __mod __pow __concat __unm __eq __lt __le assert collectgarbage dofile error getfenv getmetatable ipairs load loadfile loadstring module next pairs pcall print rawequal rawget rawset require select setfenv setmetatable tonumber tostring type unpack xpcall arg self coroutine resume yield status wrap create running debug getupvalue debug sethook getmetatable gethook setmetatable setlocal traceback setfenv getinfo setupvalue getlocal getregistry getfenv io lines write close flush open output type read stderr stdin input stdout popen tmpfile math log max acos huge ldexp pi cos tanh pow deg tan cosh sinh random randomseed frexp ceil floor rad abs sqrt modf asin min mod fmod log10 atan2 exp sin atan os exit setlocale date getenv difftime remove time clock tmpname rename execute package preload loadlib loaded loaders cpath config path seeall string sub upper len gfind rep find match char dump gmatch reverse byte format gsub lower table setn insert getn foreachi maxn foreach concat sort remove",
    },
    contains: i.concat([
      {
        className: "function",
        beginKeywords: "function",
        end: "\\)",
        contains: [
          e.inherit(e.TITLE_MODE, {
            begin: "([_a-zA-Z]\\w*\\.)*([_a-zA-Z]\\w*:)?[_a-zA-Z]\\w*",
          }),
          {
            className: "params",
            begin: "\\(",
            endsWithParent: !0,
            contains: i,
          },
        ].concat(i),
      },
      e.C_NUMBER_MODE,
      e.APOS_STRING_MODE,
      e.QUOTE_STRING_MODE,
      { className: "string", begin: t, end: n, contains: [r], relevance: 5 },
    ]),
  };
}
function IC(e) {
  const t = {
      className: "variable",
      variants: [
        {
          begin: "\\$\\(" + e.UNDERSCORE_IDENT_RE + "\\)",
          contains: [e.BACKSLASH_ESCAPE],
        },
        { begin: /\$[@%<?\^\+\*]/ },
      ],
    },
    n = {
      className: "string",
      begin: /"/,
      end: /"/,
      contains: [e.BACKSLASH_ESCAPE, t],
    },
    r = {
      className: "variable",
      begin: /\$\([\w-]+\s/,
      end: /\)/,
      keywords: {
        built_in:
          "subst patsubst strip findstring filter filter-out sort word wordlist firstword lastword dir notdir suffix basename addsuffix addprefix join wildcard realpath abspath error warning shell origin flavor foreach if or and call eval file value",
      },
      contains: [t, n],
    },
    i = { begin: "^" + e.UNDERSCORE_IDENT_RE + "\\s*(?=[:+?]?=)" },
    o = {
      className: "meta",
      begin: /^\.PHONY:/,
      end: /$/,
      keywords: { $pattern: /[\.\w]+/, keyword: ".PHONY" },
    },
    l = { className: "section", begin: /^[^\s]+:/, end: /$/, contains: [t] };
  return {
    name: "Makefile",
    aliases: ["mk", "mak", "make"],
    keywords: {
      $pattern: /[\w-]+/,
      keyword:
        "define endef undefine ifdef ifndef ifeq ifneq else endif include -include sinclude override export unexport private vpath",
    },
    contains: [e.HASH_COMMENT_MODE, t, n, r, i, o, l],
  };
}
function MC(e) {
  const t = e.regex,
    n = { begin: /<\/?[A-Za-z_]/, end: ">", subLanguage: "xml", relevance: 0 },
    r = { begin: "^[-\\*]{3,}", end: "$" },
    i = {
      className: "code",
      variants: [
        { begin: "(`{3,})[^`](.|\\n)*?\\1`*[ ]*" },
        { begin: "(~{3,})[^~](.|\\n)*?\\1~*[ ]*" },
        { begin: "```", end: "```+[ ]*$" },
        { begin: "~~~", end: "~~~+[ ]*$" },
        { begin: "`.+?`" },
        {
          begin: "(?=^( {4}|\\t))",
          contains: [{ begin: "^( {4}|\\t)", end: "(\\n)$" }],
          relevance: 0,
        },
      ],
    },
    o = {
      className: "bullet",
      begin: "^[ 	]*([*+-]|(\\d+\\.))(?=\\s+)",
      end: "\\s+",
      excludeEnd: !0,
    },
    l = {
      begin: /^\[[^\n]+\]:/,
      returnBegin: !0,
      contains: [
        {
          className: "symbol",
          begin: /\[/,
          end: /\]/,
          excludeBegin: !0,
          excludeEnd: !0,
        },
        { className: "link", begin: /:\s*/, end: /$/, excludeBegin: !0 },
      ],
    },
    a = /[A-Za-z][A-Za-z0-9+.-]*/,
    s = {
      variants: [
        { begin: /\[.+?\]\[.*?\]/, relevance: 0 },
        {
          begin:
            /\[.+?\]\(((data|javascript|mailto):|(?:http|ftp)s?:\/\/).*?\)/,
          relevance: 2,
        },
        { begin: t.concat(/\[.+?\]\(/, a, /:\/\/.*?\)/), relevance: 2 },
        { begin: /\[.+?\]\([./?&#].*?\)/, relevance: 1 },
        { begin: /\[.*?\]\(.*?\)/, relevance: 0 },
      ],
      returnBegin: !0,
      contains: [
        { match: /\[(?=\])/ },
        {
          className: "string",
          relevance: 0,
          begin: "\\[",
          end: "\\]",
          excludeBegin: !0,
          returnEnd: !0,
        },
        {
          className: "link",
          relevance: 0,
          begin: "\\]\\(",
          end: "\\)",
          excludeBegin: !0,
          excludeEnd: !0,
        },
        {
          className: "symbol",
          relevance: 0,
          begin: "\\]\\[",
          end: "\\]",
          excludeBegin: !0,
          excludeEnd: !0,
        },
      ],
    },
    u = {
      className: "strong",
      contains: [],
      variants: [
        { begin: /_{2}(?!\s)/, end: /_{2}/ },
        { begin: /\*{2}(?!\s)/, end: /\*{2}/ },
      ],
    },
    d = {
      className: "emphasis",
      contains: [],
      variants: [
        { begin: /\*(?![*\s])/, end: /\*/ },
        { begin: /_(?![_\s])/, end: /_/, relevance: 0 },
      ],
    },
    c = e.inherit(u, { contains: [] }),
    f = e.inherit(d, { contains: [] });
  (u.contains.push(f), d.contains.push(c));
  let p = [n, s];
  return (
    [u, d, c, f].forEach((h) => {
      h.contains = h.contains.concat(p);
    }),
    (p = p.concat(u, d)),
    {
      name: "Markdown",
      aliases: ["md", "mkdown", "mkd"],
      contains: [
        {
          className: "section",
          variants: [
            { begin: "^#{1,6}", end: "$", contains: p },
            {
              begin: "(?=^.+?\\n[=-]{2,}$)",
              contains: [
                { begin: "^[=-]*$" },
                { begin: "^", end: "\\n", contains: p },
              ],
            },
          ],
        },
        n,
        o,
        u,
        d,
        { className: "quote", begin: "^>\\s+", contains: p, end: "$" },
        i,
        r,
        s,
        l,
        {
          scope: "literal",
          match: /&([a-zA-Z0-9]+|#[0-9]{1,7}|#[Xx][0-9a-fA-F]{1,6});/,
        },
      ],
    }
  );
}
function LC(e) {
  const t = {
      className: "built_in",
      begin:
        "\\b(AV|CA|CF|CG|CI|CL|CM|CN|CT|MK|MP|MTK|MTL|NS|SCN|SK|UI|WK|XC)\\w+",
    },
    n = /[a-zA-Z@][a-zA-Z0-9_]*/,
    a = {
      "variable.language": ["this", "super"],
      $pattern: n,
      keyword: [
        "while",
        "export",
        "sizeof",
        "typedef",
        "const",
        "struct",
        "for",
        "union",
        "volatile",
        "static",
        "mutable",
        "if",
        "do",
        "return",
        "goto",
        "enum",
        "else",
        "break",
        "extern",
        "asm",
        "case",
        "default",
        "register",
        "explicit",
        "typename",
        "switch",
        "continue",
        "inline",
        "readonly",
        "assign",
        "readwrite",
        "self",
        "@synchronized",
        "id",
        "typeof",
        "nonatomic",
        "IBOutlet",
        "IBAction",
        "strong",
        "weak",
        "copy",
        "in",
        "out",
        "inout",
        "bycopy",
        "byref",
        "oneway",
        "__strong",
        "__weak",
        "__block",
        "__autoreleasing",
        "@private",
        "@protected",
        "@public",
        "@try",
        "@property",
        "@end",
        "@throw",
        "@catch",
        "@finally",
        "@autoreleasepool",
        "@synthesize",
        "@dynamic",
        "@selector",
        "@optional",
        "@required",
        "@encode",
        "@package",
        "@import",
        "@defs",
        "@compatibility_alias",
        "__bridge",
        "__bridge_transfer",
        "__bridge_retained",
        "__bridge_retain",
        "__covariant",
        "__contravariant",
        "__kindof",
        "_Nonnull",
        "_Nullable",
        "_Null_unspecified",
        "__FUNCTION__",
        "__PRETTY_FUNCTION__",
        "__attribute__",
        "getter",
        "setter",
        "retain",
        "unsafe_unretained",
        "nonnull",
        "nullable",
        "null_unspecified",
        "null_resettable",
        "class",
        "instancetype",
        "NS_DESIGNATED_INITIALIZER",
        "NS_UNAVAILABLE",
        "NS_REQUIRES_SUPER",
        "NS_RETURNS_INNER_POINTER",
        "NS_INLINE",
        "NS_AVAILABLE",
        "NS_DEPRECATED",
        "NS_ENUM",
        "NS_OPTIONS",
        "NS_SWIFT_UNAVAILABLE",
        "NS_ASSUME_NONNULL_BEGIN",
        "NS_ASSUME_NONNULL_END",
        "NS_REFINED_FOR_SWIFT",
        "NS_SWIFT_NAME",
        "NS_SWIFT_NOTHROW",
        "NS_DURING",
        "NS_HANDLER",
        "NS_ENDHANDLER",
        "NS_VALUERETURN",
        "NS_VOIDRETURN",
      ],
      literal: ["false", "true", "FALSE", "TRUE", "nil", "YES", "NO", "NULL"],
      built_in: [
        "dispatch_once_t",
        "dispatch_queue_t",
        "dispatch_sync",
        "dispatch_async",
        "dispatch_once",
      ],
      type: [
        "int",
        "float",
        "char",
        "unsigned",
        "signed",
        "short",
        "long",
        "double",
        "wchar_t",
        "unichar",
        "void",
        "bool",
        "BOOL",
        "id|0",
        "_Bool",
      ],
    },
    s = {
      $pattern: n,
      keyword: ["@interface", "@class", "@protocol", "@implementation"],
    };
  return {
    name: "Objective-C",
    aliases: ["mm", "objc", "obj-c", "obj-c++", "objective-c++"],
    keywords: a,
    illegal: "</",
    contains: [
      t,
      e.C_LINE_COMMENT_MODE,
      e.C_BLOCK_COMMENT_MODE,
      e.C_NUMBER_MODE,
      e.QUOTE_STRING_MODE,
      e.APOS_STRING_MODE,
      {
        className: "string",
        variants: [
          {
            begin: '@"',
            end: '"',
            illegal: "\\n",
            contains: [e.BACKSLASH_ESCAPE],
          },
        ],
      },
      {
        className: "meta",
        begin: /#\s*[a-z]+\b/,
        end: /$/,
        keywords: {
          keyword:
            "if else elif endif define undef warning error line pragma ifdef ifndef include",
        },
        contains: [
          { begin: /\\\n/, relevance: 0 },
          e.inherit(e.QUOTE_STRING_MODE, { className: "string" }),
          { className: "string", begin: /<.*?>/, end: /$/, illegal: "\\n" },
          e.C_LINE_COMMENT_MODE,
          e.C_BLOCK_COMMENT_MODE,
        ],
      },
      {
        className: "class",
        begin: "(" + s.keyword.join("|") + ")\\b",
        end: /(\{|$)/,
        excludeEnd: !0,
        keywords: s,
        contains: [e.UNDERSCORE_TITLE_MODE],
      },
      { begin: "\\." + e.UNDERSCORE_IDENT_RE, relevance: 0 },
    ],
  };
}
function DC(e) {
  const t = e.regex,
    n = [
      "abs",
      "accept",
      "alarm",
      "and",
      "atan2",
      "bind",
      "binmode",
      "bless",
      "break",
      "caller",
      "chdir",
      "chmod",
      "chomp",
      "chop",
      "chown",
      "chr",
      "chroot",
      "class",
      "close",
      "closedir",
      "connect",
      "continue",
      "cos",
      "crypt",
      "dbmclose",
      "dbmopen",
      "defined",
      "delete",
      "die",
      "do",
      "dump",
      "each",
      "else",
      "elsif",
      "endgrent",
      "endhostent",
      "endnetent",
      "endprotoent",
      "endpwent",
      "endservent",
      "eof",
      "eval",
      "exec",
      "exists",
      "exit",
      "exp",
      "fcntl",
      "field",
      "fileno",
      "flock",
      "for",
      "foreach",
      "fork",
      "format",
      "formline",
      "getc",
      "getgrent",
      "getgrgid",
      "getgrnam",
      "gethostbyaddr",
      "gethostbyname",
      "gethostent",
      "getlogin",
      "getnetbyaddr",
      "getnetbyname",
      "getnetent",
      "getpeername",
      "getpgrp",
      "getpriority",
      "getprotobyname",
      "getprotobynumber",
      "getprotoent",
      "getpwent",
      "getpwnam",
      "getpwuid",
      "getservbyname",
      "getservbyport",
      "getservent",
      "getsockname",
      "getsockopt",
      "given",
      "glob",
      "gmtime",
      "goto",
      "grep",
      "gt",
      "hex",
      "if",
      "index",
      "int",
      "ioctl",
      "join",
      "keys",
      "kill",
      "last",
      "lc",
      "lcfirst",
      "length",
      "link",
      "listen",
      "local",
      "localtime",
      "log",
      "lstat",
      "lt",
      "ma",
      "map",
      "method",
      "mkdir",
      "msgctl",
      "msgget",
      "msgrcv",
      "msgsnd",
      "my",
      "ne",
      "next",
      "no",
      "not",
      "oct",
      "open",
      "opendir",
      "or",
      "ord",
      "our",
      "pack",
      "package",
      "pipe",
      "pop",
      "pos",
      "print",
      "printf",
      "prototype",
      "push",
      "q|0",
      "qq",
      "quotemeta",
      "qw",
      "qx",
      "rand",
      "read",
      "readdir",
      "readline",
      "readlink",
      "readpipe",
      "recv",
      "redo",
      "ref",
      "rename",
      "require",
      "reset",
      "return",
      "reverse",
      "rewinddir",
      "rindex",
      "rmdir",
      "say",
      "scalar",
      "seek",
      "seekdir",
      "select",
      "semctl",
      "semget",
      "semop",
      "send",
      "setgrent",
      "sethostent",
      "setnetent",
      "setpgrp",
      "setpriority",
      "setprotoent",
      "setpwent",
      "setservent",
      "setsockopt",
      "shift",
      "shmctl",
      "shmget",
      "shmread",
      "shmwrite",
      "shutdown",
      "sin",
      "sleep",
      "socket",
      "socketpair",
      "sort",
      "splice",
      "split",
      "sprintf",
      "sqrt",
      "srand",
      "stat",
      "state",
      "study",
      "sub",
      "substr",
      "symlink",
      "syscall",
      "sysopen",
      "sysread",
      "sysseek",
      "system",
      "syswrite",
      "tell",
      "telldir",
      "tie",
      "tied",
      "time",
      "times",
      "tr",
      "truncate",
      "uc",
      "ucfirst",
      "umask",
      "undef",
      "unless",
      "unlink",
      "unpack",
      "unshift",
      "untie",
      "until",
      "use",
      "utime",
      "values",
      "vec",
      "wait",
      "waitpid",
      "wantarray",
      "warn",
      "when",
      "while",
      "write",
      "x|0",
      "xor",
      "y|0",
    ],
    r = /[dualxmsipngr]{0,12}/,
    i = { $pattern: /[\w.]+/, keyword: n.join(" ") },
    o = { className: "subst", begin: "[$@]\\{", end: "\\}", keywords: i },
    l = { begin: /->\{/, end: /\}/ },
    a = { scope: "attr", match: /\s+:\s*\w+(\s*\(.*?\))?/ },
    s = {
      scope: "variable",
      variants: [
        { begin: /\$\d/ },
        {
          begin: t.concat(
            /[$%@](?!")(\^\w\b|#\w+(::\w+)*|\{\w+\}|\w+(::\w*)*)/,
            "(?![A-Za-z])(?![@$%])",
          ),
        },
        { begin: /[$%@](?!")[^\s\w{=]|\$=/, relevance: 0 },
      ],
      contains: [a],
    },
    u = {
      className: "number",
      variants: [
        { match: /0?\.[0-9][0-9_]+\b/ },
        { match: /\bv?(0|[1-9][0-9_]*(\.[0-9_]+)?|[1-9][0-9_]*)\b/ },
        { match: /\b0[0-7][0-7_]*\b/ },
        { match: /\b0x[0-9a-fA-F][0-9a-fA-F_]*\b/ },
        { match: /\b0b[0-1][0-1_]*\b/ },
      ],
      relevance: 0,
    },
    d = [e.BACKSLASH_ESCAPE, o, s],
    c = [/!/, /\//, /\|/, /\?/, /'/, /"/, /#/],
    f = (y, E, h = "\\1") => {
      const m = h === "\\1" ? h : t.concat(h, E);
      return t.concat(
        t.concat("(?:", y, ")"),
        E,
        /(?:\\.|[^\\\/])*?/,
        m,
        /(?:\\.|[^\\\/])*?/,
        h,
        r,
      );
    },
    p = (y, E, h) =>
      t.concat(t.concat("(?:", y, ")"), E, /(?:\\.|[^\\\/])*?/, h, r),
    g = [
      s,
      e.HASH_COMMENT_MODE,
      e.COMMENT(/^=\w/, /=cut/, { endsWithParent: !0 }),
      l,
      {
        className: "string",
        contains: d,
        variants: [
          { begin: "q[qwxr]?\\s*\\(", end: "\\)", relevance: 5 },
          { begin: "q[qwxr]?\\s*\\[", end: "\\]", relevance: 5 },
          { begin: "q[qwxr]?\\s*\\{", end: "\\}", relevance: 5 },
          { begin: "q[qwxr]?\\s*\\|", end: "\\|", relevance: 5 },
          { begin: "q[qwxr]?\\s*<", end: ">", relevance: 5 },
          { begin: "qw\\s+q", end: "q", relevance: 5 },
          { begin: "'", end: "'", contains: [e.BACKSLASH_ESCAPE] },
          { begin: '"', end: '"' },
          { begin: "`", end: "`", contains: [e.BACKSLASH_ESCAPE] },
          { begin: /\{\w+\}/, relevance: 0 },
          { begin: "-?\\w+\\s*=>", relevance: 0 },
        ],
      },
      u,
      {
        begin:
          "(\\/\\/|" +
          e.RE_STARTERS_RE +
          "|\\b(split|return|print|reverse|grep)\\b)\\s*",
        keywords: "split return print reverse grep",
        relevance: 0,
        contains: [
          e.HASH_COMMENT_MODE,
          {
            className: "regexp",
            variants: [
              { begin: f("s|tr|y", t.either(...c, { capture: !0 })) },
              { begin: f("s|tr|y", "\\(", "\\)") },
              { begin: f("s|tr|y", "\\[", "\\]") },
              { begin: f("s|tr|y", "\\{", "\\}") },
            ],
            relevance: 2,
          },
          {
            className: "regexp",
            variants: [
              { begin: /(m|qr)\/\//, relevance: 0 },
              { begin: p("(?:m|qr)?", /\//, /\//) },
              { begin: p("m|qr", t.either(...c, { capture: !0 }), /\1/) },
              { begin: p("m|qr", /\(/, /\)/) },
              { begin: p("m|qr", /\[/, /\]/) },
              { begin: p("m|qr", /\{/, /\}/) },
            ],
          },
        ],
      },
      {
        className: "function",
        beginKeywords: "sub method",
        end: "(\\s*\\(.*?\\))?[;{]",
        excludeEnd: !0,
        relevance: 5,
        contains: [e.TITLE_MODE, a],
      },
      {
        className: "class",
        beginKeywords: "class",
        end: "[;{]",
        excludeEnd: !0,
        relevance: 5,
        contains: [e.TITLE_MODE, a, u],
      },
      { begin: "-\\w\\b", relevance: 0 },
      {
        begin: "^__DATA__$",
        end: "^__END__$",
        subLanguage: "mojolicious",
        contains: [{ begin: "^@@.*", end: "$", className: "comment" }],
      },
    ];
  return (
    (o.contains = g),
    (l.contains = g),
    { name: "Perl", aliases: ["pl", "pm"], keywords: i, contains: g }
  );
}
function PC(e) {
  const t = e.regex,
    n = /(?![A-Za-z0-9])(?![$])/,
    r = t.concat(/[a-zA-Z_\x7f-\xff][a-zA-Z0-9_\x7f-\xff]*/, n),
    i = t.concat(
      /(\\?[A-Z][a-z0-9_\x7f-\xff]+|\\?[A-Z]+(?=[A-Z][a-z0-9_\x7f-\xff])){1,}/,
      n,
    ),
    o = t.concat(/[A-Z]+/, n),
    l = { scope: "variable", match: "\\$+" + r },
    a = {
      scope: "meta",
      variants: [
        { begin: /<\?php/, relevance: 10 },
        { begin: /<\?=/ },
        { begin: /<\?/, relevance: 0.1 },
        { begin: /\?>/ },
      ],
    },
    s = {
      scope: "subst",
      variants: [{ begin: /\$\w+/ }, { begin: /\{\$/, end: /\}/ }],
    },
    u = e.inherit(e.APOS_STRING_MODE, { illegal: null }),
    d = e.inherit(e.QUOTE_STRING_MODE, {
      illegal: null,
      contains: e.QUOTE_STRING_MODE.contains.concat(s),
    }),
    c = {
      begin: /<<<[ \t]*(?:(\w+)|"(\w+)")\n/,
      end: /[ \t]*(\w+)\b/,
      contains: e.QUOTE_STRING_MODE.contains.concat(s),
      "on:begin": (V, G) => {
        G.data._beginMatch = V[1] || V[2];
      },
      "on:end": (V, G) => {
        G.data._beginMatch !== V[1] && G.ignoreMatch();
      },
    },
    f = e.END_SAME_AS_BEGIN({
      begin: /<<<[ \t]*'(\w+)'\n/,
      end: /[ \t]*(\w+)\b/,
    }),
    p = `[ 	
]`,
    g = { scope: "string", variants: [d, u, c, f] },
    y = {
      scope: "number",
      variants: [
        { begin: "\\b0[bB][01]+(?:_[01]+)*\\b" },
        { begin: "\\b0[oO][0-7]+(?:_[0-7]+)*\\b" },
        { begin: "\\b0[xX][\\da-fA-F]+(?:_[\\da-fA-F]+)*\\b" },
        {
          begin:
            "(?:\\b\\d+(?:_\\d+)*(\\.(?:\\d+(?:_\\d+)*))?|\\B\\.\\d+)(?:[eE][+-]?\\d+)?",
        },
      ],
      relevance: 0,
    },
    E = ["false", "null", "true"],
    h = [
      "__CLASS__",
      "__DIR__",
      "__FILE__",
      "__FUNCTION__",
      "__COMPILER_HALT_OFFSET__",
      "__LINE__",
      "__METHOD__",
      "__NAMESPACE__",
      "__TRAIT__",
      "die",
      "echo",
      "exit",
      "include",
      "include_once",
      "print",
      "require",
      "require_once",
      "array",
      "abstract",
      "and",
      "as",
      "binary",
      "bool",
      "boolean",
      "break",
      "callable",
      "case",
      "catch",
      "class",
      "clone",
      "const",
      "continue",
      "declare",
      "default",
      "do",
      "double",
      "else",
      "elseif",
      "empty",
      "enddeclare",
      "endfor",
      "endforeach",
      "endif",
      "endswitch",
      "endwhile",
      "enum",
      "eval",
      "extends",
      "final",
      "finally",
      "float",
      "for",
      "foreach",
      "from",
      "global",
      "goto",
      "if",
      "implements",
      "instanceof",
      "insteadof",
      "int",
      "integer",
      "interface",
      "isset",
      "iterable",
      "list",
      "match|0",
      "mixed",
      "new",
      "never",
      "object",
      "or",
      "private",
      "protected",
      "public",
      "readonly",
      "real",
      "return",
      "string",
      "switch",
      "throw",
      "trait",
      "try",
      "unset",
      "use",
      "var",
      "void",
      "while",
      "xor",
      "yield",
    ],
    m = [
      "Error|0",
      "AppendIterator",
      "ArgumentCountError",
      "ArithmeticError",
      "ArrayIterator",
      "ArrayObject",
      "AssertionError",
      "BadFunctionCallException",
      "BadMethodCallException",
      "CachingIterator",
      "CallbackFilterIterator",
      "CompileError",
      "Countable",
      "DirectoryIterator",
      "DivisionByZeroError",
      "DomainException",
      "EmptyIterator",
      "ErrorException",
      "Exception",
      "FilesystemIterator",
      "FilterIterator",
      "GlobIterator",
      "InfiniteIterator",
      "InvalidArgumentException",
      "IteratorIterator",
      "LengthException",
      "LimitIterator",
      "LogicException",
      "MultipleIterator",
      "NoRewindIterator",
      "OutOfBoundsException",
      "OutOfRangeException",
      "OuterIterator",
      "OverflowException",
      "ParentIterator",
      "ParseError",
      "RangeException",
      "RecursiveArrayIterator",
      "RecursiveCachingIterator",
      "RecursiveCallbackFilterIterator",
      "RecursiveDirectoryIterator",
      "RecursiveFilterIterator",
      "RecursiveIterator",
      "RecursiveIteratorIterator",
      "RecursiveRegexIterator",
      "RecursiveTreeIterator",
      "RegexIterator",
      "RuntimeException",
      "SeekableIterator",
      "SplDoublyLinkedList",
      "SplFileInfo",
      "SplFileObject",
      "SplFixedArray",
      "SplHeap",
      "SplMaxHeap",
      "SplMinHeap",
      "SplObjectStorage",
      "SplObserver",
      "SplPriorityQueue",
      "SplQueue",
      "SplStack",
      "SplSubject",
      "SplTempFileObject",
      "TypeError",
      "UnderflowException",
      "UnexpectedValueException",
      "UnhandledMatchError",
      "ArrayAccess",
      "BackedEnum",
      "Closure",
      "Fiber",
      "Generator",
      "Iterator",
      "IteratorAggregate",
      "Serializable",
      "Stringable",
      "Throwable",
      "Traversable",
      "UnitEnum",
      "WeakReference",
      "WeakMap",
      "Directory",
      "__PHP_Incomplete_Class",
      "parent",
      "php_user_filter",
      "self",
      "static",
      "stdClass",
    ],
    _ = {
      keyword: h,
      literal: ((V) => {
        const G = [];
        return (
          V.forEach((R) => {
            (G.push(R),
              R.toLowerCase() === R
                ? G.push(R.toUpperCase())
                : G.push(R.toLowerCase()));
          }),
          G
        );
      })(E),
      built_in: m,
    },
    N = (V) => V.map((G) => G.replace(/\|\d+$/, "")),
    x = {
      variants: [
        {
          match: [
            /new/,
            t.concat(p, "+"),
            t.concat("(?!", N(m).join("\\b|"), "\\b)"),
            i,
          ],
          scope: { 1: "keyword", 4: "title.class" },
        },
      ],
    },
    O = t.concat(r, "\\b(?!\\()"),
    I = {
      variants: [
        {
          match: [t.concat(/::/, t.lookahead(/(?!class\b)/)), O],
          scope: { 2: "variable.constant" },
        },
        { match: [/::/, /class/], scope: { 2: "variable.language" } },
        {
          match: [i, t.concat(/::/, t.lookahead(/(?!class\b)/)), O],
          scope: { 1: "title.class", 3: "variable.constant" },
        },
        {
          match: [i, t.concat("::", t.lookahead(/(?!class\b)/))],
          scope: { 1: "title.class" },
        },
        {
          match: [i, /::/, /class/],
          scope: { 1: "title.class", 3: "variable.language" },
        },
      ],
    },
    U = {
      scope: "attr",
      match: t.concat(r, t.lookahead(":"), t.lookahead(/(?!::)/)),
    },
    S = {
      relevance: 0,
      begin: /\(/,
      end: /\)/,
      keywords: _,
      contains: [U, l, I, e.C_BLOCK_COMMENT_MODE, g, y, x],
    },
    F = {
      relevance: 0,
      match: [
        /\b/,
        t.concat(
          "(?!fn\\b|function\\b|",
          N(h).join("\\b|"),
          "|",
          N(m).join("\\b|"),
          "\\b)",
        ),
        r,
        t.concat(p, "*"),
        t.lookahead(/(?=\()/),
      ],
      scope: { 3: "title.function.invoke" },
      contains: [S],
    };
  S.contains.push(F);
  const L = [U, I, e.C_BLOCK_COMMENT_MODE, g, y, x],
    Q = {
      begin: t.concat(/#\[\s*\\?/, t.either(i, o)),
      beginScope: "meta",
      end: /]/,
      endScope: "meta",
      keywords: { literal: E, keyword: ["new", "array"] },
      contains: [
        {
          begin: /\[/,
          end: /]/,
          keywords: { literal: E, keyword: ["new", "array"] },
          contains: ["self", ...L],
        },
        ...L,
        { scope: "meta", variants: [{ match: i }, { match: o }] },
      ],
    };
  return {
    case_insensitive: !1,
    keywords: _,
    contains: [
      Q,
      e.HASH_COMMENT_MODE,
      e.COMMENT("//", "$"),
      e.COMMENT("/\\*", "\\*/", {
        contains: [{ scope: "doctag", match: "@[A-Za-z]+" }],
      }),
      {
        match: /__halt_compiler\(\);/,
        keywords: "__halt_compiler",
        starts: {
          scope: "comment",
          end: e.MATCH_NOTHING_RE,
          contains: [{ match: /\?>/, scope: "meta", endsParent: !0 }],
        },
      },
      a,
      { scope: "variable.language", match: /\$this\b/ },
      l,
      F,
      I,
      {
        match: [/const/, /\s/, r],
        scope: { 1: "keyword", 3: "variable.constant" },
      },
      x,
      {
        scope: "function",
        relevance: 0,
        beginKeywords: "fn function",
        end: /[;{]/,
        excludeEnd: !0,
        illegal: "[$%\\[]",
        contains: [
          { beginKeywords: "use" },
          e.UNDERSCORE_TITLE_MODE,
          { begin: "=>", endsParent: !0 },
          {
            scope: "params",
            begin: "\\(",
            end: "\\)",
            excludeBegin: !0,
            excludeEnd: !0,
            keywords: _,
            contains: ["self", Q, l, I, e.C_BLOCK_COMMENT_MODE, g, y],
          },
        ],
      },
      {
        scope: "class",
        variants: [
          { beginKeywords: "enum", illegal: /[($"]/ },
          { beginKeywords: "class interface trait", illegal: /[:($"]/ },
        ],
        relevance: 0,
        end: /\{/,
        excludeEnd: !0,
        contains: [
          { beginKeywords: "extends implements" },
          e.UNDERSCORE_TITLE_MODE,
        ],
      },
      {
        beginKeywords: "namespace",
        relevance: 0,
        end: ";",
        illegal: /[.']/,
        contains: [
          e.inherit(e.UNDERSCORE_TITLE_MODE, { scope: "title.class" }),
        ],
      },
      {
        beginKeywords: "use",
        relevance: 0,
        end: ";",
        contains: [
          { match: /\b(as|const|function)\b/, scope: "keyword" },
          e.UNDERSCORE_TITLE_MODE,
        ],
      },
      g,
      y,
    ],
  };
}
function zC(e) {
  return {
    name: "PHP template",
    subLanguage: "xml",
    contains: [
      {
        begin: /<\?(php|=)?/,
        end: /\?>/,
        subLanguage: "php",
        contains: [
          { begin: "/\\*", end: "\\*/", skip: !0 },
          { begin: 'b"', end: '"', skip: !0 },
          { begin: "b'", end: "'", skip: !0 },
          e.inherit(e.APOS_STRING_MODE, {
            illegal: null,
            className: null,
            contains: null,
            skip: !0,
          }),
          e.inherit(e.QUOTE_STRING_MODE, {
            illegal: null,
            className: null,
            contains: null,
            skip: !0,
          }),
        ],
      },
    ],
  };
}
function FC(e) {
  return {
    name: "Plain text",
    aliases: ["text", "txt"],
    disableAutodetect: !0,
  };
}
function BC(e) {
  const t = e.regex,
    n = new RegExp("[\\p{XID_Start}_]\\p{XID_Continue}*", "u"),
    r = [
      "and",
      "as",
      "assert",
      "async",
      "await",
      "break",
      "case",
      "class",
      "continue",
      "def",
      "del",
      "elif",
      "else",
      "except",
      "finally",
      "for",
      "from",
      "global",
      "if",
      "import",
      "in",
      "is",
      "lambda",
      "match",
      "nonlocal|10",
      "not",
      "or",
      "pass",
      "raise",
      "return",
      "try",
      "while",
      "with",
      "yield",
    ],
    a = {
      $pattern: /[A-Za-z]\w+|__\w+__/,
      keyword: r,
      built_in: [
        "__import__",
        "abs",
        "all",
        "any",
        "ascii",
        "bin",
        "bool",
        "breakpoint",
        "bytearray",
        "bytes",
        "callable",
        "chr",
        "classmethod",
        "compile",
        "complex",
        "delattr",
        "dict",
        "dir",
        "divmod",
        "enumerate",
        "eval",
        "exec",
        "filter",
        "float",
        "format",
        "frozenset",
        "getattr",
        "globals",
        "hasattr",
        "hash",
        "help",
        "hex",
        "id",
        "input",
        "int",
        "isinstance",
        "issubclass",
        "iter",
        "len",
        "list",
        "locals",
        "map",
        "max",
        "memoryview",
        "min",
        "next",
        "object",
        "oct",
        "open",
        "ord",
        "pow",
        "print",
        "property",
        "range",
        "repr",
        "reversed",
        "round",
        "set",
        "setattr",
        "slice",
        "sorted",
        "staticmethod",
        "str",
        "sum",
        "super",
        "tuple",
        "type",
        "vars",
        "zip",
      ],
      literal: [
        "__debug__",
        "Ellipsis",
        "False",
        "None",
        "NotImplemented",
        "True",
      ],
      type: [
        "Any",
        "Callable",
        "Coroutine",
        "Dict",
        "List",
        "Literal",
        "Generic",
        "Optional",
        "Sequence",
        "Set",
        "Tuple",
        "Type",
        "Union",
      ],
    },
    s = { className: "meta", begin: /^(>>>|\.\.\.) / },
    u = {
      className: "subst",
      begin: /\{/,
      end: /\}/,
      keywords: a,
      illegal: /#/,
    },
    d = { begin: /\{\{/, relevance: 0 },
    c = {
      className: "string",
      contains: [e.BACKSLASH_ESCAPE],
      variants: [
        {
          begin: /([uU]|[bB]|[rR]|[bB][rR]|[rR][bB])?'''/,
          end: /'''/,
          contains: [e.BACKSLASH_ESCAPE, s],
          relevance: 10,
        },
        {
          begin: /([uU]|[bB]|[rR]|[bB][rR]|[rR][bB])?"""/,
          end: /"""/,
          contains: [e.BACKSLASH_ESCAPE, s],
          relevance: 10,
        },
        {
          begin: /([fF][rR]|[rR][fF]|[fF])'''/,
          end: /'''/,
          contains: [e.BACKSLASH_ESCAPE, s, d, u],
        },
        {
          begin: /([fF][rR]|[rR][fF]|[fF])"""/,
          end: /"""/,
          contains: [e.BACKSLASH_ESCAPE, s, d, u],
        },
        { begin: /([uU]|[rR])'/, end: /'/, relevance: 10 },
        { begin: /([uU]|[rR])"/, end: /"/, relevance: 10 },
        { begin: /([bB]|[bB][rR]|[rR][bB])'/, end: /'/ },
        { begin: /([bB]|[bB][rR]|[rR][bB])"/, end: /"/ },
        {
          begin: /([fF][rR]|[rR][fF]|[fF])'/,
          end: /'/,
          contains: [e.BACKSLASH_ESCAPE, d, u],
        },
        {
          begin: /([fF][rR]|[rR][fF]|[fF])"/,
          end: /"/,
          contains: [e.BACKSLASH_ESCAPE, d, u],
        },
        e.APOS_STRING_MODE,
        e.QUOTE_STRING_MODE,
      ],
    },
    f = "[0-9](_?[0-9])*",
    p = `(\\b(${f}))?\\.(${f})|\\b(${f})\\.`,
    g = `\\b|${r.join("|")}`,
    y = {
      className: "number",
      relevance: 0,
      variants: [
        { begin: `(\\b(${f})|(${p}))[eE][+-]?(${f})[jJ]?(?=${g})` },
        { begin: `(${p})[jJ]?` },
        { begin: `\\b([1-9](_?[0-9])*|0+(_?0)*)[lLjJ]?(?=${g})` },
        { begin: `\\b0[bB](_?[01])+[lL]?(?=${g})` },
        { begin: `\\b0[oO](_?[0-7])+[lL]?(?=${g})` },
        { begin: `\\b0[xX](_?[0-9a-fA-F])+[lL]?(?=${g})` },
        { begin: `\\b(${f})[jJ](?=${g})` },
      ],
    },
    E = {
      className: "comment",
      begin: t.lookahead(/# type:/),
      end: /$/,
      keywords: a,
      contains: [
        { begin: /# type:/ },
        { begin: /#/, end: /\b\B/, endsWithParent: !0 },
      ],
    },
    h = {
      className: "params",
      variants: [
        { className: "", begin: /\(\s*\)/, skip: !0 },
        {
          begin: /\(/,
          end: /\)/,
          excludeBegin: !0,
          excludeEnd: !0,
          keywords: a,
          contains: ["self", s, y, c, e.HASH_COMMENT_MODE],
        },
      ],
    };
  return (
    (u.contains = [c, y, s]),
    {
      name: "Python",
      aliases: ["py", "gyp", "ipython"],
      unicodeRegex: !0,
      keywords: a,
      illegal: /(<\/|\?)|=>/,
      contains: [
        s,
        y,
        { scope: "variable.language", match: /\bself\b/ },
        { beginKeywords: "if", relevance: 0 },
        { match: /\bor\b/, scope: "keyword" },
        c,
        E,
        e.HASH_COMMENT_MODE,
        {
          match: [/\bdef/, /\s+/, n],
          scope: { 1: "keyword", 3: "title.function" },
          contains: [h],
        },
        {
          variants: [
            { match: [/\bclass/, /\s+/, n, /\s*/, /\(\s*/, n, /\s*\)/] },
            { match: [/\bclass/, /\s+/, n] },
          ],
          scope: { 1: "keyword", 3: "title.class", 6: "title.class.inherited" },
        },
        {
          className: "meta",
          begin: /^[\t ]*@/,
          end: /(?=#)|$/,
          contains: [y, h, c],
        },
      ],
    }
  );
}
function UC(e) {
  return {
    aliases: ["pycon"],
    contains: [
      {
        className: "meta.prompt",
        starts: { end: / |$/, starts: { end: "$", subLanguage: "python" } },
        variants: [{ begin: /^>>>(?=[ ]|$)/ }, { begin: /^\.\.\.(?=[ ]|$)/ }],
      },
    ],
  };
}
function $C(e) {
  const t = e.regex,
    n = /(?:(?:[a-zA-Z]|\.[._a-zA-Z])[._a-zA-Z0-9]*)|\.(?!\d)/,
    r = t.either(
      /0[xX][0-9a-fA-F]+\.[0-9a-fA-F]*[pP][+-]?\d+i?/,
      /0[xX][0-9a-fA-F]+(?:[pP][+-]?\d+)?[Li]?/,
      /(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?[Li]?/,
    ),
    i = /[=!<>:]=|\|\||&&|:::?|<-|<<-|->>|->|\|>|[-+*\/?!$&|:<=>@^~]|\*\*/,
    o = t.either(/[()]/, /[{}]/, /\[\[/, /[[\]]/, /\\/, /,/);
  return {
    name: "R",
    keywords: {
      $pattern: n,
      keyword: "function if in break next repeat else for while",
      literal:
        "NULL NA TRUE FALSE Inf NaN NA_integer_|10 NA_real_|10 NA_character_|10 NA_complex_|10",
      built_in:
        "LETTERS letters month.abb month.name pi T F abs acos acosh all any anyNA Arg as.call as.character as.complex as.double as.environment as.integer as.logical as.null.default as.numeric as.raw asin asinh atan atanh attr attributes baseenv browser c call ceiling class Conj cos cosh cospi cummax cummin cumprod cumsum digamma dim dimnames emptyenv exp expression floor forceAndCall gamma gc.time globalenv Im interactive invisible is.array is.atomic is.call is.character is.complex is.double is.environment is.expression is.finite is.function is.infinite is.integer is.language is.list is.logical is.matrix is.na is.name is.nan is.null is.numeric is.object is.pairlist is.raw is.recursive is.single is.symbol lazyLoadDBfetch length lgamma list log max min missing Mod names nargs nzchar oldClass on.exit pos.to.env proc.time prod quote range Re rep retracemem return round seq_along seq_len seq.int sign signif sin sinh sinpi sqrt standardGeneric substitute sum switch tan tanh tanpi tracemem trigamma trunc unclass untracemem UseMethod xtfrm",
    },
    contains: [
      e.COMMENT(/#'/, /$/, {
        contains: [
          {
            scope: "doctag",
            match: /@examples/,
            starts: {
              end: t.lookahead(t.either(/\n^#'\s*(?=@[a-zA-Z]+)/, /\n^(?!#')/)),
              endsParent: !0,
            },
          },
          {
            scope: "doctag",
            begin: "@param",
            end: /$/,
            contains: [
              {
                scope: "variable",
                variants: [{ match: n }, { match: /`(?:\\.|[^`\\])+`/ }],
                endsParent: !0,
              },
            ],
          },
          { scope: "doctag", match: /@[a-zA-Z]+/ },
          { scope: "keyword", match: /\\[a-zA-Z]+/ },
        ],
      }),
      e.HASH_COMMENT_MODE,
      {
        scope: "string",
        contains: [e.BACKSLASH_ESCAPE],
        variants: [
          e.END_SAME_AS_BEGIN({ begin: /[rR]"(-*)\(/, end: /\)(-*)"/ }),
          e.END_SAME_AS_BEGIN({ begin: /[rR]"(-*)\{/, end: /\}(-*)"/ }),
          e.END_SAME_AS_BEGIN({ begin: /[rR]"(-*)\[/, end: /\](-*)"/ }),
          e.END_SAME_AS_BEGIN({ begin: /[rR]'(-*)\(/, end: /\)(-*)'/ }),
          e.END_SAME_AS_BEGIN({ begin: /[rR]'(-*)\{/, end: /\}(-*)'/ }),
          e.END_SAME_AS_BEGIN({ begin: /[rR]'(-*)\[/, end: /\](-*)'/ }),
          { begin: '"', end: '"', relevance: 0 },
          { begin: "'", end: "'", relevance: 0 },
        ],
      },
      {
        relevance: 0,
        variants: [
          { scope: { 1: "operator", 2: "number" }, match: [i, r] },
          { scope: { 1: "operator", 2: "number" }, match: [/%[^%]*%/, r] },
          { scope: { 1: "punctuation", 2: "number" }, match: [o, r] },
          { scope: { 2: "number" }, match: [/[^a-zA-Z0-9._]|^/, r] },
        ],
      },
      { scope: { 3: "operator" }, match: [n, /\s+/, /<-/, /\s+/] },
      {
        scope: "operator",
        relevance: 0,
        variants: [{ match: i }, { match: /%[^%]*%/ }],
      },
      { scope: "punctuation", relevance: 0, match: o },
      { begin: "`", end: "`", contains: [{ begin: /\\./ }] },
    ],
  };
}
function HC(e) {
  const t = e.regex,
    n =
      "([a-zA-Z_]\\w*[!?=]?|[-+~]@|<<|>>|=~|===?|<=>|[<>]=?|\\*\\*|[-/+%^&*~`|]|\\[\\]=?)",
    r = t.either(/\b([A-Z]+[a-z0-9]+)+/, /\b([A-Z]+[a-z0-9]+)+[A-Z]+/),
    i = t.concat(r, /(::\w+)*/),
    l = {
      "variable.constant": ["__FILE__", "__LINE__", "__ENCODING__"],
      "variable.language": ["self", "super"],
      keyword: [
        "alias",
        "and",
        "begin",
        "BEGIN",
        "break",
        "case",
        "class",
        "defined",
        "do",
        "else",
        "elsif",
        "end",
        "END",
        "ensure",
        "for",
        "if",
        "in",
        "module",
        "next",
        "not",
        "or",
        "redo",
        "require",
        "rescue",
        "retry",
        "return",
        "then",
        "undef",
        "unless",
        "until",
        "when",
        "while",
        "yield",
        ...[
          "include",
          "extend",
          "prepend",
          "public",
          "private",
          "protected",
          "raise",
          "throw",
        ],
      ],
      built_in: [
        "proc",
        "lambda",
        "attr_accessor",
        "attr_reader",
        "attr_writer",
        "define_method",
        "private_constant",
        "module_function",
      ],
      literal: ["true", "false", "nil"],
    },
    a = { className: "doctag", begin: "@[A-Za-z]+" },
    s = { begin: "#<", end: ">" },
    u = [
      e.COMMENT("#", "$", { contains: [a] }),
      e.COMMENT("^=begin", "^=end", { contains: [a], relevance: 10 }),
      e.COMMENT("^__END__", e.MATCH_NOTHING_RE),
    ],
    d = { className: "subst", begin: /#\{/, end: /\}/, keywords: l },
    c = {
      className: "string",
      contains: [e.BACKSLASH_ESCAPE, d],
      variants: [
        { begin: /'/, end: /'/ },
        { begin: /"/, end: /"/ },
        { begin: /`/, end: /`/ },
        { begin: /%[qQwWx]?\(/, end: /\)/ },
        { begin: /%[qQwWx]?\[/, end: /\]/ },
        { begin: /%[qQwWx]?\{/, end: /\}/ },
        { begin: /%[qQwWx]?</, end: />/ },
        { begin: /%[qQwWx]?\//, end: /\// },
        { begin: /%[qQwWx]?%/, end: /%/ },
        { begin: /%[qQwWx]?-/, end: /-/ },
        { begin: /%[qQwWx]?\|/, end: /\|/ },
        { begin: /\B\?(\\\d{1,3})/ },
        { begin: /\B\?(\\x[A-Fa-f0-9]{1,2})/ },
        { begin: /\B\?(\\u\{?[A-Fa-f0-9]{1,6}\}?)/ },
        { begin: /\B\?(\\M-\\C-|\\M-\\c|\\c\\M-|\\M-|\\C-\\M-)[\x20-\x7e]/ },
        { begin: /\B\?\\(c|C-)[\x20-\x7e]/ },
        { begin: /\B\?\\?\S/ },
        {
          begin: t.concat(
            /<<[-~]?'?/,
            t.lookahead(/(\w+)(?=\W)[^\n]*\n(?:[^\n]*\n)*?\s*\1\b/),
          ),
          contains: [
            e.END_SAME_AS_BEGIN({
              begin: /(\w+)/,
              end: /(\w+)/,
              contains: [e.BACKSLASH_ESCAPE, d],
            }),
          ],
        },
      ],
    },
    f = "[1-9](_?[0-9])*|0",
    p = "[0-9](_?[0-9])*",
    g = {
      className: "number",
      relevance: 0,
      variants: [
        { begin: `\\b(${f})(\\.(${p}))?([eE][+-]?(${p})|r)?i?\\b` },
        { begin: "\\b0[dD][0-9](_?[0-9])*r?i?\\b" },
        { begin: "\\b0[bB][0-1](_?[0-1])*r?i?\\b" },
        { begin: "\\b0[oO][0-7](_?[0-7])*r?i?\\b" },
        { begin: "\\b0[xX][0-9a-fA-F](_?[0-9a-fA-F])*r?i?\\b" },
        { begin: "\\b0(_?[0-7])+r?i?\\b" },
      ],
    },
    y = {
      variants: [
        { match: /\(\)/ },
        {
          className: "params",
          begin: /\(/,
          end: /(?=\))/,
          excludeBegin: !0,
          endsParent: !0,
          keywords: l,
        },
      ],
    },
    x = [
      c,
      {
        variants: [
          { match: [/class\s+/, i, /\s+<\s+/, i] },
          { match: [/\b(class|module)\s+/, i] },
        ],
        scope: { 2: "title.class", 4: "title.class.inherited" },
        keywords: l,
      },
      {
        match: [/(include|extend)\s+/, i],
        scope: { 2: "title.class" },
        keywords: l,
      },
      { relevance: 0, match: [i, /\.new[. (]/], scope: { 1: "title.class" } },
      {
        relevance: 0,
        match: /\b[A-Z][A-Z_0-9]+\b/,
        className: "variable.constant",
      },
      { relevance: 0, match: r, scope: "title.class" },
      {
        match: [/def/, /\s+/, n],
        scope: { 1: "keyword", 3: "title.function" },
        contains: [y],
      },
      { begin: e.IDENT_RE + "::" },
      {
        className: "symbol",
        begin: e.UNDERSCORE_IDENT_RE + "(!|\\?)?:",
        relevance: 0,
      },
      {
        className: "symbol",
        begin: ":(?!\\s)",
        contains: [c, { begin: n }],
        relevance: 0,
      },
      g,
      {
        className: "variable",
        begin: "(\\$\\W)|((\\$|@@?)(\\w+))(?=[^@$?])(?![A-Za-z])(?![@$?'])",
      },
      {
        className: "params",
        begin: /\|(?!=)/,
        end: /\|/,
        excludeBegin: !0,
        excludeEnd: !0,
        relevance: 0,
        keywords: l,
      },
      {
        begin: "(" + e.RE_STARTERS_RE + "|unless)\\s*",
        keywords: "unless",
        contains: [
          {
            className: "regexp",
            contains: [e.BACKSLASH_ESCAPE, d],
            illegal: /\n/,
            variants: [
              { begin: "/", end: "/[a-z]*" },
              { begin: /%r\{/, end: /\}[a-z]*/ },
              { begin: "%r\\(", end: "\\)[a-z]*" },
              { begin: "%r!", end: "![a-z]*" },
              { begin: "%r\\[", end: "\\][a-z]*" },
            ],
          },
        ].concat(s, u),
        relevance: 0,
      },
    ].concat(s, u);
  ((d.contains = x), (y.contains = x));
  const S = [
    { begin: /^\s*=>/, starts: { end: "$", contains: x } },
    {
      className: "meta.prompt",
      begin:
        "^(" +
        "[>?]>" +
        "|" +
        "[\\w#]+\\(\\w+\\):\\d+:\\d+[>*]" +
        "|" +
        "(\\w+-)?\\d+\\.\\d+\\.\\d+(p\\d+)?[^\\d][^>]+>" +
        ")(?=[ ])",
      starts: { end: "$", keywords: l, contains: x },
    },
  ];
  return (
    u.unshift(s),
    {
      name: "Ruby",
      aliases: ["rb", "gemspec", "podspec", "thor", "irb"],
      keywords: l,
      illegal: /\/\*/,
      contains: [e.SHEBANG({ binary: "ruby" })].concat(S).concat(u).concat(x),
    }
  );
}
function jC(e) {
  const t = e.regex,
    n = /(r#)?/,
    r = t.concat(n, e.UNDERSCORE_IDENT_RE),
    i = t.concat(n, e.IDENT_RE),
    o = {
      className: "title.function.invoke",
      relevance: 0,
      begin: t.concat(
        /\b/,
        /(?!let|for|while|if|else|match\b)/,
        i,
        t.lookahead(/\s*\(/),
      ),
    },
    l = "([ui](8|16|32|64|128|size)|f(32|64))?",
    a = [
      "abstract",
      "as",
      "async",
      "await",
      "become",
      "box",
      "break",
      "const",
      "continue",
      "crate",
      "do",
      "dyn",
      "else",
      "enum",
      "extern",
      "false",
      "final",
      "fn",
      "for",
      "if",
      "impl",
      "in",
      "let",
      "loop",
      "macro",
      "match",
      "mod",
      "move",
      "mut",
      "override",
      "priv",
      "pub",
      "ref",
      "return",
      "self",
      "Self",
      "static",
      "struct",
      "super",
      "trait",
      "true",
      "try",
      "type",
      "typeof",
      "union",
      "unsafe",
      "unsized",
      "use",
      "virtual",
      "where",
      "while",
      "yield",
    ],
    s = ["true", "false", "Some", "None", "Ok", "Err"],
    u = [
      "drop ",
      "Copy",
      "Send",
      "Sized",
      "Sync",
      "Drop",
      "Fn",
      "FnMut",
      "FnOnce",
      "ToOwned",
      "Clone",
      "Debug",
      "PartialEq",
      "PartialOrd",
      "Eq",
      "Ord",
      "AsRef",
      "AsMut",
      "Into",
      "From",
      "Default",
      "Iterator",
      "Extend",
      "IntoIterator",
      "DoubleEndedIterator",
      "ExactSizeIterator",
      "SliceConcatExt",
      "ToString",
      "assert!",
      "assert_eq!",
      "bitflags!",
      "bytes!",
      "cfg!",
      "col!",
      "concat!",
      "concat_idents!",
      "debug_assert!",
      "debug_assert_eq!",
      "env!",
      "eprintln!",
      "panic!",
      "file!",
      "format!",
      "format_args!",
      "include_bytes!",
      "include_str!",
      "line!",
      "local_data_key!",
      "module_path!",
      "option_env!",
      "print!",
      "println!",
      "select!",
      "stringify!",
      "try!",
      "unimplemented!",
      "unreachable!",
      "vec!",
      "write!",
      "writeln!",
      "macro_rules!",
      "assert_ne!",
      "debug_assert_ne!",
    ],
    d = [
      "i8",
      "i16",
      "i32",
      "i64",
      "i128",
      "isize",
      "u8",
      "u16",
      "u32",
      "u64",
      "u128",
      "usize",
      "f32",
      "f64",
      "str",
      "char",
      "bool",
      "Box",
      "Option",
      "Result",
      "String",
      "Vec",
    ];
  return {
    name: "Rust",
    aliases: ["rs"],
    keywords: {
      $pattern: e.IDENT_RE + "!?",
      type: d,
      keyword: a,
      literal: s,
      built_in: u,
    },
    illegal: "</",
    contains: [
      e.C_LINE_COMMENT_MODE,
      e.COMMENT("/\\*", "\\*/", { contains: ["self"] }),
      e.inherit(e.QUOTE_STRING_MODE, { begin: /b?"/, illegal: null }),
      { className: "symbol", begin: /'[a-zA-Z_][a-zA-Z0-9_]*(?!')/ },
      {
        scope: "string",
        variants: [
          { begin: /b?r(#*)"(.|\n)*?"\1(?!#)/ },
          {
            begin: /b?'/,
            end: /'/,
            contains: [
              { scope: "char.escape", match: /\\('|\w|x\w{2}|u\w{4}|U\w{8})/ },
            ],
          },
        ],
      },
      {
        className: "number",
        variants: [
          { begin: "\\b0b([01_]+)" + l },
          { begin: "\\b0o([0-7_]+)" + l },
          { begin: "\\b0x([A-Fa-f0-9_]+)" + l },
          { begin: "\\b(\\d[\\d_]*(\\.[0-9_]+)?([eE][+-]?[0-9_]+)?)" + l },
        ],
        relevance: 0,
      },
      {
        begin: [/fn/, /\s+/, r],
        className: { 1: "keyword", 3: "title.function" },
      },
      {
        className: "meta",
        begin: "#!?\\[",
        end: "\\]",
        contains: [
          {
            className: "string",
            begin: /"/,
            end: /"/,
            contains: [e.BACKSLASH_ESCAPE],
          },
        ],
      },
      {
        begin: [/let/, /\s+/, /(?:mut\s+)?/, r],
        className: { 1: "keyword", 3: "keyword", 4: "variable" },
      },
      {
        begin: [/for/, /\s+/, r, /\s+/, /in/],
        className: { 1: "keyword", 3: "variable", 5: "keyword" },
      },
      {
        begin: [/type/, /\s+/, r],
        className: { 1: "keyword", 3: "title.class" },
      },
      {
        begin: [/(?:trait|enum|struct|union|impl|for)/, /\s+/, r],
        className: { 1: "keyword", 3: "title.class" },
      },
      {
        begin: e.IDENT_RE + "::",
        keywords: { keyword: "Self", built_in: u, type: d },
      },
      { className: "punctuation", begin: "->" },
      o,
    ],
  };
}
const WC = (e) => ({
    IMPORTANT: { scope: "meta", begin: "!important" },
    BLOCK_COMMENT: e.C_BLOCK_COMMENT_MODE,
    HEXCOLOR: {
      scope: "number",
      begin: /#(([0-9a-fA-F]{3,4})|(([0-9a-fA-F]{2}){3,4}))\b/,
    },
    FUNCTION_DISPATCH: { className: "built_in", begin: /[\w-]+(?=\()/ },
    ATTRIBUTE_SELECTOR_MODE: {
      scope: "selector-attr",
      begin: /\[/,
      end: /\]/,
      illegal: "$",
      contains: [e.APOS_STRING_MODE, e.QUOTE_STRING_MODE],
    },
    CSS_NUMBER_MODE: {
      scope: "number",
      begin:
        e.NUMBER_RE +
        "(%|em|ex|ch|rem|vw|vh|vmin|vmax|cm|mm|in|pt|pc|px|deg|grad|rad|turn|s|ms|Hz|kHz|dpi|dpcm|dppx)?",
      relevance: 0,
    },
    CSS_VARIABLE: { className: "attr", begin: /--[A-Za-z_][A-Za-z0-9_-]*/ },
  }),
  GC = [
    "a",
    "abbr",
    "address",
    "article",
    "aside",
    "audio",
    "b",
    "blockquote",
    "body",
    "button",
    "canvas",
    "caption",
    "cite",
    "code",
    "dd",
    "del",
    "details",
    "dfn",
    "div",
    "dl",
    "dt",
    "em",
    "fieldset",
    "figcaption",
    "figure",
    "footer",
    "form",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "header",
    "hgroup",
    "html",
    "i",
    "iframe",
    "img",
    "input",
    "ins",
    "kbd",
    "label",
    "legend",
    "li",
    "main",
    "mark",
    "menu",
    "nav",
    "object",
    "ol",
    "optgroup",
    "option",
    "p",
    "picture",
    "q",
    "quote",
    "samp",
    "section",
    "select",
    "source",
    "span",
    "strong",
    "summary",
    "sup",
    "table",
    "tbody",
    "td",
    "textarea",
    "tfoot",
    "th",
    "thead",
    "time",
    "tr",
    "ul",
    "var",
    "video",
  ],
  KC = [
    "defs",
    "g",
    "marker",
    "mask",
    "pattern",
    "svg",
    "switch",
    "symbol",
    "feBlend",
    "feColorMatrix",
    "feComponentTransfer",
    "feComposite",
    "feConvolveMatrix",
    "feDiffuseLighting",
    "feDisplacementMap",
    "feFlood",
    "feGaussianBlur",
    "feImage",
    "feMerge",
    "feMorphology",
    "feOffset",
    "feSpecularLighting",
    "feTile",
    "feTurbulence",
    "linearGradient",
    "radialGradient",
    "stop",
    "circle",
    "ellipse",
    "image",
    "line",
    "path",
    "polygon",
    "polyline",
    "rect",
    "text",
    "use",
    "textPath",
    "tspan",
    "foreignObject",
    "clipPath",
  ],
  VC = [...GC, ...KC],
  qC = [
    "any-hover",
    "any-pointer",
    "aspect-ratio",
    "color",
    "color-gamut",
    "color-index",
    "device-aspect-ratio",
    "device-height",
    "device-width",
    "display-mode",
    "forced-colors",
    "grid",
    "height",
    "hover",
    "inverted-colors",
    "monochrome",
    "orientation",
    "overflow-block",
    "overflow-inline",
    "pointer",
    "prefers-color-scheme",
    "prefers-contrast",
    "prefers-reduced-motion",
    "prefers-reduced-transparency",
    "resolution",
    "scan",
    "scripting",
    "update",
    "width",
    "min-width",
    "max-width",
    "min-height",
    "max-height",
  ]
    .sort()
    .reverse(),
  YC = [
    "active",
    "any-link",
    "blank",
    "checked",
    "current",
    "default",
    "defined",
    "dir",
    "disabled",
    "drop",
    "empty",
    "enabled",
    "first",
    "first-child",
    "first-of-type",
    "fullscreen",
    "future",
    "focus",
    "focus-visible",
    "focus-within",
    "has",
    "host",
    "host-context",
    "hover",
    "indeterminate",
    "in-range",
    "invalid",
    "is",
    "lang",
    "last-child",
    "last-of-type",
    "left",
    "link",
    "local-link",
    "not",
    "nth-child",
    "nth-col",
    "nth-last-child",
    "nth-last-col",
    "nth-last-of-type",
    "nth-of-type",
    "only-child",
    "only-of-type",
    "optional",
    "out-of-range",
    "past",
    "placeholder-shown",
    "read-only",
    "read-write",
    "required",
    "right",
    "root",
    "scope",
    "target",
    "target-within",
    "user-invalid",
    "valid",
    "visited",
    "where",
  ]
    .sort()
    .reverse(),
  QC = [
    "after",
    "backdrop",
    "before",
    "cue",
    "cue-region",
    "first-letter",
    "first-line",
    "grammar-error",
    "marker",
    "part",
    "placeholder",
    "selection",
    "slotted",
    "spelling-error",
  ]
    .sort()
    .reverse(),
  ZC = [
    "accent-color",
    "align-content",
    "align-items",
    "align-self",
    "alignment-baseline",
    "all",
    "anchor-name",
    "animation",
    "animation-composition",
    "animation-delay",
    "animation-direction",
    "animation-duration",
    "animation-fill-mode",
    "animation-iteration-count",
    "animation-name",
    "animation-play-state",
    "animation-range",
    "animation-range-end",
    "animation-range-start",
    "animation-timeline",
    "animation-timing-function",
    "appearance",
    "aspect-ratio",
    "backdrop-filter",
    "backface-visibility",
    "background",
    "background-attachment",
    "background-blend-mode",
    "background-clip",
    "background-color",
    "background-image",
    "background-origin",
    "background-position",
    "background-position-x",
    "background-position-y",
    "background-repeat",
    "background-size",
    "baseline-shift",
    "block-size",
    "border",
    "border-block",
    "border-block-color",
    "border-block-end",
    "border-block-end-color",
    "border-block-end-style",
    "border-block-end-width",
    "border-block-start",
    "border-block-start-color",
    "border-block-start-style",
    "border-block-start-width",
    "border-block-style",
    "border-block-width",
    "border-bottom",
    "border-bottom-color",
    "border-bottom-left-radius",
    "border-bottom-right-radius",
    "border-bottom-style",
    "border-bottom-width",
    "border-collapse",
    "border-color",
    "border-end-end-radius",
    "border-end-start-radius",
    "border-image",
    "border-image-outset",
    "border-image-repeat",
    "border-image-slice",
    "border-image-source",
    "border-image-width",
    "border-inline",
    "border-inline-color",
    "border-inline-end",
    "border-inline-end-color",
    "border-inline-end-style",
    "border-inline-end-width",
    "border-inline-start",
    "border-inline-start-color",
    "border-inline-start-style",
    "border-inline-start-width",
    "border-inline-style",
    "border-inline-width",
    "border-left",
    "border-left-color",
    "border-left-style",
    "border-left-width",
    "border-radius",
    "border-right",
    "border-right-color",
    "border-right-style",
    "border-right-width",
    "border-spacing",
    "border-start-end-radius",
    "border-start-start-radius",
    "border-style",
    "border-top",
    "border-top-color",
    "border-top-left-radius",
    "border-top-right-radius",
    "border-top-style",
    "border-top-width",
    "border-width",
    "bottom",
    "box-align",
    "box-decoration-break",
    "box-direction",
    "box-flex",
    "box-flex-group",
    "box-lines",
    "box-ordinal-group",
    "box-orient",
    "box-pack",
    "box-shadow",
    "box-sizing",
    "break-after",
    "break-before",
    "break-inside",
    "caption-side",
    "caret-color",
    "clear",
    "clip",
    "clip-path",
    "clip-rule",
    "color",
    "color-interpolation",
    "color-interpolation-filters",
    "color-profile",
    "color-rendering",
    "color-scheme",
    "column-count",
    "column-fill",
    "column-gap",
    "column-rule",
    "column-rule-color",
    "column-rule-style",
    "column-rule-width",
    "column-span",
    "column-width",
    "columns",
    "contain",
    "contain-intrinsic-block-size",
    "contain-intrinsic-height",
    "contain-intrinsic-inline-size",
    "contain-intrinsic-size",
    "contain-intrinsic-width",
    "container",
    "container-name",
    "container-type",
    "content",
    "content-visibility",
    "counter-increment",
    "counter-reset",
    "counter-set",
    "cue",
    "cue-after",
    "cue-before",
    "cursor",
    "cx",
    "cy",
    "direction",
    "display",
    "dominant-baseline",
    "empty-cells",
    "enable-background",
    "field-sizing",
    "fill",
    "fill-opacity",
    "fill-rule",
    "filter",
    "flex",
    "flex-basis",
    "flex-direction",
    "flex-flow",
    "flex-grow",
    "flex-shrink",
    "flex-wrap",
    "float",
    "flood-color",
    "flood-opacity",
    "flow",
    "font",
    "font-display",
    "font-family",
    "font-feature-settings",
    "font-kerning",
    "font-language-override",
    "font-optical-sizing",
    "font-palette",
    "font-size",
    "font-size-adjust",
    "font-smooth",
    "font-smoothing",
    "font-stretch",
    "font-style",
    "font-synthesis",
    "font-synthesis-position",
    "font-synthesis-small-caps",
    "font-synthesis-style",
    "font-synthesis-weight",
    "font-variant",
    "font-variant-alternates",
    "font-variant-caps",
    "font-variant-east-asian",
    "font-variant-emoji",
    "font-variant-ligatures",
    "font-variant-numeric",
    "font-variant-position",
    "font-variation-settings",
    "font-weight",
    "forced-color-adjust",
    "gap",
    "glyph-orientation-horizontal",
    "glyph-orientation-vertical",
    "grid",
    "grid-area",
    "grid-auto-columns",
    "grid-auto-flow",
    "grid-auto-rows",
    "grid-column",
    "grid-column-end",
    "grid-column-start",
    "grid-gap",
    "grid-row",
    "grid-row-end",
    "grid-row-start",
    "grid-template",
    "grid-template-areas",
    "grid-template-columns",
    "grid-template-rows",
    "hanging-punctuation",
    "height",
    "hyphenate-character",
    "hyphenate-limit-chars",
    "hyphens",
    "icon",
    "image-orientation",
    "image-rendering",
    "image-resolution",
    "ime-mode",
    "initial-letter",
    "initial-letter-align",
    "inline-size",
    "inset",
    "inset-area",
    "inset-block",
    "inset-block-end",
    "inset-block-start",
    "inset-inline",
    "inset-inline-end",
    "inset-inline-start",
    "isolation",
    "justify-content",
    "justify-items",
    "justify-self",
    "kerning",
    "left",
    "letter-spacing",
    "lighting-color",
    "line-break",
    "line-height",
    "line-height-step",
    "list-style",
    "list-style-image",
    "list-style-position",
    "list-style-type",
    "margin",
    "margin-block",
    "margin-block-end",
    "margin-block-start",
    "margin-bottom",
    "margin-inline",
    "margin-inline-end",
    "margin-inline-start",
    "margin-left",
    "margin-right",
    "margin-top",
    "margin-trim",
    "marker",
    "marker-end",
    "marker-mid",
    "marker-start",
    "marks",
    "mask",
    "mask-border",
    "mask-border-mode",
    "mask-border-outset",
    "mask-border-repeat",
    "mask-border-slice",
    "mask-border-source",
    "mask-border-width",
    "mask-clip",
    "mask-composite",
    "mask-image",
    "mask-mode",
    "mask-origin",
    "mask-position",
    "mask-repeat",
    "mask-size",
    "mask-type",
    "masonry-auto-flow",
    "math-depth",
    "math-shift",
    "math-style",
    "max-block-size",
    "max-height",
    "max-inline-size",
    "max-width",
    "min-block-size",
    "min-height",
    "min-inline-size",
    "min-width",
    "mix-blend-mode",
    "nav-down",
    "nav-index",
    "nav-left",
    "nav-right",
    "nav-up",
    "none",
    "normal",
    "object-fit",
    "object-position",
    "offset",
    "offset-anchor",
    "offset-distance",
    "offset-path",
    "offset-position",
    "offset-rotate",
    "opacity",
    "order",
    "orphans",
    "outline",
    "outline-color",
    "outline-offset",
    "outline-style",
    "outline-width",
    "overflow",
    "overflow-anchor",
    "overflow-block",
    "overflow-clip-margin",
    "overflow-inline",
    "overflow-wrap",
    "overflow-x",
    "overflow-y",
    "overlay",
    "overscroll-behavior",
    "overscroll-behavior-block",
    "overscroll-behavior-inline",
    "overscroll-behavior-x",
    "overscroll-behavior-y",
    "padding",
    "padding-block",
    "padding-block-end",
    "padding-block-start",
    "padding-bottom",
    "padding-inline",
    "padding-inline-end",
    "padding-inline-start",
    "padding-left",
    "padding-right",
    "padding-top",
    "page",
    "page-break-after",
    "page-break-before",
    "page-break-inside",
    "paint-order",
    "pause",
    "pause-after",
    "pause-before",
    "perspective",
    "perspective-origin",
    "place-content",
    "place-items",
    "place-self",
    "pointer-events",
    "position",
    "position-anchor",
    "position-visibility",
    "print-color-adjust",
    "quotes",
    "r",
    "resize",
    "rest",
    "rest-after",
    "rest-before",
    "right",
    "rotate",
    "row-gap",
    "ruby-align",
    "ruby-position",
    "scale",
    "scroll-behavior",
    "scroll-margin",
    "scroll-margin-block",
    "scroll-margin-block-end",
    "scroll-margin-block-start",
    "scroll-margin-bottom",
    "scroll-margin-inline",
    "scroll-margin-inline-end",
    "scroll-margin-inline-start",
    "scroll-margin-left",
    "scroll-margin-right",
    "scroll-margin-top",
    "scroll-padding",
    "scroll-padding-block",
    "scroll-padding-block-end",
    "scroll-padding-block-start",
    "scroll-padding-bottom",
    "scroll-padding-inline",
    "scroll-padding-inline-end",
    "scroll-padding-inline-start",
    "scroll-padding-left",
    "scroll-padding-right",
    "scroll-padding-top",
    "scroll-snap-align",
    "scroll-snap-stop",
    "scroll-snap-type",
    "scroll-timeline",
    "scroll-timeline-axis",
    "scroll-timeline-name",
    "scrollbar-color",
    "scrollbar-gutter",
    "scrollbar-width",
    "shape-image-threshold",
    "shape-margin",
    "shape-outside",
    "shape-rendering",
    "speak",
    "speak-as",
    "src",
    "stop-color",
    "stop-opacity",
    "stroke",
    "stroke-dasharray",
    "stroke-dashoffset",
    "stroke-linecap",
    "stroke-linejoin",
    "stroke-miterlimit",
    "stroke-opacity",
    "stroke-width",
    "tab-size",
    "table-layout",
    "text-align",
    "text-align-all",
    "text-align-last",
    "text-anchor",
    "text-combine-upright",
    "text-decoration",
    "text-decoration-color",
    "text-decoration-line",
    "text-decoration-skip",
    "text-decoration-skip-ink",
    "text-decoration-style",
    "text-decoration-thickness",
    "text-emphasis",
    "text-emphasis-color",
    "text-emphasis-position",
    "text-emphasis-style",
    "text-indent",
    "text-justify",
    "text-orientation",
    "text-overflow",
    "text-rendering",
    "text-shadow",
    "text-size-adjust",
    "text-transform",
    "text-underline-offset",
    "text-underline-position",
    "text-wrap",
    "text-wrap-mode",
    "text-wrap-style",
    "timeline-scope",
    "top",
    "touch-action",
    "transform",
    "transform-box",
    "transform-origin",
    "transform-style",
    "transition",
    "transition-behavior",
    "transition-delay",
    "transition-duration",
    "transition-property",
    "transition-timing-function",
    "translate",
    "unicode-bidi",
    "user-modify",
    "user-select",
    "vector-effect",
    "vertical-align",
    "view-timeline",
    "view-timeline-axis",
    "view-timeline-inset",
    "view-timeline-name",
    "view-transition-name",
    "visibility",
    "voice-balance",
    "voice-duration",
    "voice-family",
    "voice-pitch",
    "voice-range",
    "voice-rate",
    "voice-stress",
    "voice-volume",
    "white-space",
    "white-space-collapse",
    "widows",
    "width",
    "will-change",
    "word-break",
    "word-spacing",
    "word-wrap",
    "writing-mode",
    "x",
    "y",
    "z-index",
    "zoom",
  ]
    .sort()
    .reverse();
function XC(e) {
  const t = WC(e),
    n = QC,
    r = YC,
    i = "@[a-z-]+",
    o = "and or not only",
    a = {
      className: "variable",
      begin: "(\\$" + "[a-zA-Z-][a-zA-Z0-9_-]*" + ")\\b",
      relevance: 0,
    };
  return {
    name: "SCSS",
    case_insensitive: !0,
    illegal: "[=/|']",
    contains: [
      e.C_LINE_COMMENT_MODE,
      e.C_BLOCK_COMMENT_MODE,
      t.CSS_NUMBER_MODE,
      { className: "selector-id", begin: "#[A-Za-z0-9_-]+", relevance: 0 },
      { className: "selector-class", begin: "\\.[A-Za-z0-9_-]+", relevance: 0 },
      t.ATTRIBUTE_SELECTOR_MODE,
      {
        className: "selector-tag",
        begin: "\\b(" + VC.join("|") + ")\\b",
        relevance: 0,
      },
      { className: "selector-pseudo", begin: ":(" + r.join("|") + ")" },
      { className: "selector-pseudo", begin: ":(:)?(" + n.join("|") + ")" },
      a,
      { begin: /\(/, end: /\)/, contains: [t.CSS_NUMBER_MODE] },
      t.CSS_VARIABLE,
      { className: "attribute", begin: "\\b(" + ZC.join("|") + ")\\b" },
      {
        begin:
          "\\b(whitespace|wait|w-resize|visible|vertical-text|vertical-ideographic|uppercase|upper-roman|upper-alpha|underline|transparent|top|thin|thick|text|text-top|text-bottom|tb-rl|table-header-group|table-footer-group|sw-resize|super|strict|static|square|solid|small-caps|separate|se-resize|scroll|s-resize|rtl|row-resize|ridge|right|repeat|repeat-y|repeat-x|relative|progress|pointer|overline|outside|outset|oblique|nowrap|not-allowed|normal|none|nw-resize|no-repeat|no-drop|newspaper|ne-resize|n-resize|move|middle|medium|ltr|lr-tb|lowercase|lower-roman|lower-alpha|loose|list-item|line|line-through|line-edge|lighter|left|keep-all|justify|italic|inter-word|inter-ideograph|inside|inset|inline|inline-block|inherit|inactive|ideograph-space|ideograph-parenthesis|ideograph-numeric|ideograph-alpha|horizontal|hidden|help|hand|groove|fixed|ellipsis|e-resize|double|dotted|distribute|distribute-space|distribute-letter|distribute-all-lines|disc|disabled|default|decimal|dashed|crosshair|collapse|col-resize|circle|char|center|capitalize|break-word|break-all|bottom|both|bolder|bold|block|bidi-override|below|baseline|auto|always|all-scroll|absolute|table|table-cell)\\b",
      },
      {
        begin: /:/,
        end: /[;}{]/,
        relevance: 0,
        contains: [
          t.BLOCK_COMMENT,
          a,
          t.HEXCOLOR,
          t.CSS_NUMBER_MODE,
          e.QUOTE_STRING_MODE,
          e.APOS_STRING_MODE,
          t.IMPORTANT,
          t.FUNCTION_DISPATCH,
        ],
      },
      {
        begin: "@(page|font-face)",
        keywords: { $pattern: i, keyword: "@page @font-face" },
      },
      {
        begin: "@",
        end: "[{;]",
        returnBegin: !0,
        keywords: { $pattern: /[a-z-]+/, keyword: o, attribute: qC.join(" ") },
        contains: [
          { begin: i, className: "keyword" },
          { begin: /[a-z-]+(?=:)/, className: "attribute" },
          a,
          e.QUOTE_STRING_MODE,
          e.APOS_STRING_MODE,
          t.HEXCOLOR,
          t.CSS_NUMBER_MODE,
        ],
      },
      t.FUNCTION_DISPATCH,
    ],
  };
}
function JC(e) {
  return {
    name: "Shell Session",
    aliases: ["console", "shellsession"],
    contains: [
      {
        className: "meta.prompt",
        begin: /^\s{0,3}[/~\w\d[\]()@-]*[>%$#][ ]?/,
        starts: { end: /[^\\](?=\s*$)/, subLanguage: "bash" },
      },
    ],
  };
}
function eT(e) {
  const t = e.regex,
    n = e.COMMENT("--", "$"),
    r = {
      scope: "string",
      variants: [{ begin: /'/, end: /'/, contains: [{ match: /''/ }] }],
    },
    i = { begin: /"/, end: /"/, contains: [{ match: /""/ }] },
    o = ["true", "false", "unknown"],
    l = [
      "double precision",
      "large object",
      "with timezone",
      "without timezone",
    ],
    a = [
      "bigint",
      "binary",
      "blob",
      "boolean",
      "char",
      "character",
      "clob",
      "date",
      "dec",
      "decfloat",
      "decimal",
      "float",
      "int",
      "integer",
      "interval",
      "nchar",
      "nclob",
      "national",
      "numeric",
      "real",
      "row",
      "smallint",
      "time",
      "timestamp",
      "varchar",
      "varying",
      "varbinary",
    ],
    s = ["add", "asc", "collation", "desc", "final", "first", "last", "view"],
    u = [
      "abs",
      "acos",
      "all",
      "allocate",
      "alter",
      "and",
      "any",
      "are",
      "array",
      "array_agg",
      "array_max_cardinality",
      "as",
      "asensitive",
      "asin",
      "asymmetric",
      "at",
      "atan",
      "atomic",
      "authorization",
      "avg",
      "begin",
      "begin_frame",
      "begin_partition",
      "between",
      "bigint",
      "binary",
      "blob",
      "boolean",
      "both",
      "by",
      "call",
      "called",
      "cardinality",
      "cascaded",
      "case",
      "cast",
      "ceil",
      "ceiling",
      "char",
      "char_length",
      "character",
      "character_length",
      "check",
      "classifier",
      "clob",
      "close",
      "coalesce",
      "collate",
      "collect",
      "column",
      "commit",
      "condition",
      "connect",
      "constraint",
      "contains",
      "convert",
      "copy",
      "corr",
      "corresponding",
      "cos",
      "cosh",
      "count",
      "covar_pop",
      "covar_samp",
      "create",
      "cross",
      "cube",
      "cume_dist",
      "current",
      "current_catalog",
      "current_date",
      "current_default_transform_group",
      "current_path",
      "current_role",
      "current_row",
      "current_schema",
      "current_time",
      "current_timestamp",
      "current_path",
      "current_role",
      "current_transform_group_for_type",
      "current_user",
      "cursor",
      "cycle",
      "date",
      "day",
      "deallocate",
      "dec",
      "decimal",
      "decfloat",
      "declare",
      "default",
      "define",
      "delete",
      "dense_rank",
      "deref",
      "describe",
      "deterministic",
      "disconnect",
      "distinct",
      "double",
      "drop",
      "dynamic",
      "each",
      "element",
      "else",
      "empty",
      "end",
      "end_frame",
      "end_partition",
      "end-exec",
      "equals",
      "escape",
      "every",
      "except",
      "exec",
      "execute",
      "exists",
      "exp",
      "external",
      "extract",
      "false",
      "fetch",
      "filter",
      "first_value",
      "float",
      "floor",
      "for",
      "foreign",
      "frame_row",
      "free",
      "from",
      "full",
      "function",
      "fusion",
      "get",
      "global",
      "grant",
      "group",
      "grouping",
      "groups",
      "having",
      "hold",
      "hour",
      "identity",
      "in",
      "indicator",
      "initial",
      "inner",
      "inout",
      "insensitive",
      "insert",
      "int",
      "integer",
      "intersect",
      "intersection",
      "interval",
      "into",
      "is",
      "join",
      "json_array",
      "json_arrayagg",
      "json_exists",
      "json_object",
      "json_objectagg",
      "json_query",
      "json_table",
      "json_table_primitive",
      "json_value",
      "lag",
      "language",
      "large",
      "last_value",
      "lateral",
      "lead",
      "leading",
      "left",
      "like",
      "like_regex",
      "listagg",
      "ln",
      "local",
      "localtime",
      "localtimestamp",
      "log",
      "log10",
      "lower",
      "match",
      "match_number",
      "match_recognize",
      "matches",
      "max",
      "member",
      "merge",
      "method",
      "min",
      "minute",
      "mod",
      "modifies",
      "module",
      "month",
      "multiset",
      "national",
      "natural",
      "nchar",
      "nclob",
      "new",
      "no",
      "none",
      "normalize",
      "not",
      "nth_value",
      "ntile",
      "null",
      "nullif",
      "numeric",
      "octet_length",
      "occurrences_regex",
      "of",
      "offset",
      "old",
      "omit",
      "on",
      "one",
      "only",
      "open",
      "or",
      "order",
      "out",
      "outer",
      "over",
      "overlaps",
      "overlay",
      "parameter",
      "partition",
      "pattern",
      "per",
      "percent",
      "percent_rank",
      "percentile_cont",
      "percentile_disc",
      "period",
      "portion",
      "position",
      "position_regex",
      "power",
      "precedes",
      "precision",
      "prepare",
      "primary",
      "procedure",
      "ptf",
      "range",
      "rank",
      "reads",
      "real",
      "recursive",
      "ref",
      "references",
      "referencing",
      "regr_avgx",
      "regr_avgy",
      "regr_count",
      "regr_intercept",
      "regr_r2",
      "regr_slope",
      "regr_sxx",
      "regr_sxy",
      "regr_syy",
      "release",
      "result",
      "return",
      "returns",
      "revoke",
      "right",
      "rollback",
      "rollup",
      "row",
      "row_number",
      "rows",
      "running",
      "savepoint",
      "scope",
      "scroll",
      "search",
      "second",
      "seek",
      "select",
      "sensitive",
      "session_user",
      "set",
      "show",
      "similar",
      "sin",
      "sinh",
      "skip",
      "smallint",
      "some",
      "specific",
      "specifictype",
      "sql",
      "sqlexception",
      "sqlstate",
      "sqlwarning",
      "sqrt",
      "start",
      "static",
      "stddev_pop",
      "stddev_samp",
      "submultiset",
      "subset",
      "substring",
      "substring_regex",
      "succeeds",
      "sum",
      "symmetric",
      "system",
      "system_time",
      "system_user",
      "table",
      "tablesample",
      "tan",
      "tanh",
      "then",
      "time",
      "timestamp",
      "timezone_hour",
      "timezone_minute",
      "to",
      "trailing",
      "translate",
      "translate_regex",
      "translation",
      "treat",
      "trigger",
      "trim",
      "trim_array",
      "true",
      "truncate",
      "uescape",
      "union",
      "unique",
      "unknown",
      "unnest",
      "update",
      "upper",
      "user",
      "using",
      "value",
      "values",
      "value_of",
      "var_pop",
      "var_samp",
      "varbinary",
      "varchar",
      "varying",
      "versioning",
      "when",
      "whenever",
      "where",
      "width_bucket",
      "window",
      "with",
      "within",
      "without",
      "year",
    ],
    d = [
      "abs",
      "acos",
      "array_agg",
      "asin",
      "atan",
      "avg",
      "cast",
      "ceil",
      "ceiling",
      "coalesce",
      "corr",
      "cos",
      "cosh",
      "count",
      "covar_pop",
      "covar_samp",
      "cume_dist",
      "dense_rank",
      "deref",
      "element",
      "exp",
      "extract",
      "first_value",
      "floor",
      "json_array",
      "json_arrayagg",
      "json_exists",
      "json_object",
      "json_objectagg",
      "json_query",
      "json_table",
      "json_table_primitive",
      "json_value",
      "lag",
      "last_value",
      "lead",
      "listagg",
      "ln",
      "log",
      "log10",
      "lower",
      "max",
      "min",
      "mod",
      "nth_value",
      "ntile",
      "nullif",
      "percent_rank",
      "percentile_cont",
      "percentile_disc",
      "position",
      "position_regex",
      "power",
      "rank",
      "regr_avgx",
      "regr_avgy",
      "regr_count",
      "regr_intercept",
      "regr_r2",
      "regr_slope",
      "regr_sxx",
      "regr_sxy",
      "regr_syy",
      "row_number",
      "sin",
      "sinh",
      "sqrt",
      "stddev_pop",
      "stddev_samp",
      "substring",
      "substring_regex",
      "sum",
      "tan",
      "tanh",
      "translate",
      "translate_regex",
      "treat",
      "trim",
      "trim_array",
      "unnest",
      "upper",
      "value_of",
      "var_pop",
      "var_samp",
      "width_bucket",
    ],
    c = [
      "current_catalog",
      "current_date",
      "current_default_transform_group",
      "current_path",
      "current_role",
      "current_schema",
      "current_transform_group_for_type",
      "current_user",
      "session_user",
      "system_time",
      "system_user",
      "current_time",
      "localtime",
      "current_timestamp",
      "localtimestamp",
    ],
    f = [
      "create table",
      "insert into",
      "primary key",
      "foreign key",
      "not null",
      "alter table",
      "add constraint",
      "grouping sets",
      "on overflow",
      "character set",
      "respect nulls",
      "ignore nulls",
      "nulls first",
      "nulls last",
      "depth first",
      "breadth first",
    ],
    p = d,
    g = [...u, ...s].filter((N) => !d.includes(N)),
    y = { scope: "variable", match: /@[a-z0-9][a-z0-9_]*/ },
    E = {
      scope: "operator",
      match: /[-+*/=%^~]|&&?|\|\|?|!=?|<(?:=>?|<|>)?|>[>=]?/,
      relevance: 0,
    },
    h = {
      match: t.concat(/\b/, t.either(...p), /\s*\(/),
      relevance: 0,
      keywords: { built_in: p },
    };
  function m(N) {
    return t.concat(
      /\b/,
      t.either(...N.map((x) => x.replace(/\s+/, "\\s+"))),
      /\b/,
    );
  }
  const b = { scope: "keyword", match: m(f), relevance: 0 };
  function _(N, { exceptions: x, when: O } = {}) {
    const I = O;
    return (
      (x = x || []),
      N.map((U) =>
        U.match(/\|\d+$/) || x.includes(U) ? U : I(U) ? `${U}|0` : U,
      )
    );
  }
  return {
    name: "SQL",
    case_insensitive: !0,
    illegal: /[{}]|<\//,
    keywords: {
      $pattern: /\b[\w\.]+/,
      keyword: _(g, { when: (N) => N.length < 3 }),
      literal: o,
      type: a,
      built_in: c,
    },
    contains: [
      { scope: "type", match: m(l) },
      b,
      h,
      y,
      r,
      i,
      e.C_NUMBER_MODE,
      e.C_BLOCK_COMMENT_MODE,
      n,
      E,
    ],
  };
}
function ly(e) {
  return e ? (typeof e == "string" ? e : e.source) : null;
}
function di(e) {
  return ue("(?=", e, ")");
}
function ue(...e) {
  return e.map((n) => ly(n)).join("");
}
function tT(e) {
  const t = e[e.length - 1];
  return typeof t == "object" && t.constructor === Object
    ? (e.splice(e.length - 1, 1), t)
    : {};
}
function je(...e) {
  return (
    "(" + (tT(e).capture ? "" : "?:") + e.map((r) => ly(r)).join("|") + ")"
  );
}
const _c = (e) => ue(/\b/, e, /\w$/.test(e) ? /\b/ : /\B/),
  nT = ["Protocol", "Type"].map(_c),
  Xf = ["init", "self"].map(_c),
  rT = ["Any", "Self"],
  Wa = [
    "actor",
    "any",
    "associatedtype",
    "async",
    "await",
    /as\?/,
    /as!/,
    "as",
    "borrowing",
    "break",
    "case",
    "catch",
    "class",
    "consume",
    "consuming",
    "continue",
    "convenience",
    "copy",
    "default",
    "defer",
    "deinit",
    "didSet",
    "distributed",
    "do",
    "dynamic",
    "each",
    "else",
    "enum",
    "extension",
    "fallthrough",
    /fileprivate\(set\)/,
    "fileprivate",
    "final",
    "for",
    "func",
    "get",
    "guard",
    "if",
    "import",
    "indirect",
    "infix",
    /init\?/,
    /init!/,
    "inout",
    /internal\(set\)/,
    "internal",
    "in",
    "is",
    "isolated",
    "nonisolated",
    "lazy",
    "let",
    "macro",
    "mutating",
    "nonmutating",
    /open\(set\)/,
    "open",
    "operator",
    "optional",
    "override",
    "package",
    "postfix",
    "precedencegroup",
    "prefix",
    /private\(set\)/,
    "private",
    "protocol",
    /public\(set\)/,
    "public",
    "repeat",
    "required",
    "rethrows",
    "return",
    "set",
    "some",
    "static",
    "struct",
    "subscript",
    "super",
    "switch",
    "throws",
    "throw",
    /try\?/,
    /try!/,
    "try",
    "typealias",
    /unowned\(safe\)/,
    /unowned\(unsafe\)/,
    "unowned",
    "var",
    "weak",
    "where",
    "while",
    "willSet",
  ],
  Jf = ["false", "nil", "true"],
  iT = [
    "assignment",
    "associativity",
    "higherThan",
    "left",
    "lowerThan",
    "none",
    "right",
  ],
  oT = [
    "#colorLiteral",
    "#column",
    "#dsohandle",
    "#else",
    "#elseif",
    "#endif",
    "#error",
    "#file",
    "#fileID",
    "#fileLiteral",
    "#filePath",
    "#function",
    "#if",
    "#imageLiteral",
    "#keyPath",
    "#line",
    "#selector",
    "#sourceLocation",
    "#warning",
  ],
  ep = [
    "abs",
    "all",
    "any",
    "assert",
    "assertionFailure",
    "debugPrint",
    "dump",
    "fatalError",
    "getVaList",
    "isKnownUniquelyReferenced",
    "max",
    "min",
    "numericCast",
    "pointwiseMax",
    "pointwiseMin",
    "precondition",
    "preconditionFailure",
    "print",
    "readLine",
    "repeatElement",
    "sequence",
    "stride",
    "swap",
    "swift_unboxFromSwiftValueWithType",
    "transcode",
    "type",
    "unsafeBitCast",
    "unsafeDowncast",
    "withExtendedLifetime",
    "withUnsafeMutablePointer",
    "withUnsafePointer",
    "withVaList",
    "withoutActuallyEscaping",
    "zip",
  ],
  ay = je(
    /[/=\-+!*%<>&|^~?]/,
    /[\u00A1-\u00A7]/,
    /[\u00A9\u00AB]/,
    /[\u00AC\u00AE]/,
    /[\u00B0\u00B1]/,
    /[\u00B6\u00BB\u00BF\u00D7\u00F7]/,
    /[\u2016-\u2017]/,
    /[\u2020-\u2027]/,
    /[\u2030-\u203E]/,
    /[\u2041-\u2053]/,
    /[\u2055-\u205E]/,
    /[\u2190-\u23FF]/,
    /[\u2500-\u2775]/,
    /[\u2794-\u2BFF]/,
    /[\u2E00-\u2E7F]/,
    /[\u3001-\u3003]/,
    /[\u3008-\u3020]/,
    /[\u3030]/,
  ),
  sy = je(
    ay,
    /[\u0300-\u036F]/,
    /[\u1DC0-\u1DFF]/,
    /[\u20D0-\u20FF]/,
    /[\uFE00-\uFE0F]/,
    /[\uFE20-\uFE2F]/,
  ),
  Ga = ue(ay, sy, "*"),
  uy = je(
    /[a-zA-Z_]/,
    /[\u00A8\u00AA\u00AD\u00AF\u00B2-\u00B5\u00B7-\u00BA]/,
    /[\u00BC-\u00BE\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u00FF]/,
    /[\u0100-\u02FF\u0370-\u167F\u1681-\u180D\u180F-\u1DBF]/,
    /[\u1E00-\u1FFF]/,
    /[\u200B-\u200D\u202A-\u202E\u203F-\u2040\u2054\u2060-\u206F]/,
    /[\u2070-\u20CF\u2100-\u218F\u2460-\u24FF\u2776-\u2793]/,
    /[\u2C00-\u2DFF\u2E80-\u2FFF]/,
    /[\u3004-\u3007\u3021-\u302F\u3031-\u303F\u3040-\uD7FF]/,
    /[\uF900-\uFD3D\uFD40-\uFDCF\uFDF0-\uFE1F\uFE30-\uFE44]/,
    /[\uFE47-\uFEFE\uFF00-\uFFFD]/,
  ),
  Cl = je(uy, /\d/, /[\u0300-\u036F\u1DC0-\u1DFF\u20D0-\u20FF\uFE20-\uFE2F]/),
  Mt = ue(uy, Cl, "*"),
  Lo = ue(/[A-Z]/, Cl, "*"),
  lT = [
    "attached",
    "autoclosure",
    ue(/convention\(/, je("swift", "block", "c"), /\)/),
    "discardableResult",
    "dynamicCallable",
    "dynamicMemberLookup",
    "escaping",
    "freestanding",
    "frozen",
    "GKInspectable",
    "IBAction",
    "IBDesignable",
    "IBInspectable",
    "IBOutlet",
    "IBSegueAction",
    "inlinable",
    "main",
    "nonobjc",
    "NSApplicationMain",
    "NSCopying",
    "NSManaged",
    ue(/objc\(/, Mt, /\)/),
    "objc",
    "objcMembers",
    "propertyWrapper",
    "requires_stored_property_inits",
    "resultBuilder",
    "Sendable",
    "testable",
    "UIApplicationMain",
    "unchecked",
    "unknown",
    "usableFromInline",
    "warn_unqualified_access",
  ],
  aT = [
    "iOS",
    "iOSApplicationExtension",
    "macOS",
    "macOSApplicationExtension",
    "macCatalyst",
    "macCatalystApplicationExtension",
    "watchOS",
    "watchOSApplicationExtension",
    "tvOS",
    "tvOSApplicationExtension",
    "swift",
  ];
function sT(e) {
  const t = { match: /\s+/, relevance: 0 },
    n = e.COMMENT("/\\*", "\\*/", { contains: ["self"] }),
    r = [e.C_LINE_COMMENT_MODE, n],
    i = { match: [/\./, je(...nT, ...Xf)], className: { 2: "keyword" } },
    o = { match: ue(/\./, je(...Wa)), relevance: 0 },
    l = Wa.filter((le) => typeof le == "string").concat(["_|0"]),
    a = Wa.filter((le) => typeof le != "string")
      .concat(rT)
      .map(_c),
    s = { variants: [{ className: "keyword", match: je(...a, ...Xf) }] },
    u = { $pattern: je(/\b\w+/, /#\w+/), keyword: l.concat(oT), literal: Jf },
    d = [i, o, s],
    c = { match: ue(/\./, je(...ep)), relevance: 0 },
    f = { className: "built_in", match: ue(/\b/, je(...ep), /(?=\()/) },
    p = [c, f],
    g = { match: /->/, relevance: 0 },
    y = {
      className: "operator",
      relevance: 0,
      variants: [{ match: Ga }, { match: `\\.(\\.|${sy})+` }],
    },
    E = [g, y],
    h = "([0-9]_*)+",
    m = "([0-9a-fA-F]_*)+",
    b = {
      className: "number",
      relevance: 0,
      variants: [
        { match: `\\b(${h})(\\.(${h}))?([eE][+-]?(${h}))?\\b` },
        { match: `\\b0x(${m})(\\.(${m}))?([pP][+-]?(${h}))?\\b` },
        { match: /\b0o([0-7]_*)+\b/ },
        { match: /\b0b([01]_*)+\b/ },
      ],
    },
    _ = (le = "") => ({
      className: "subst",
      variants: [
        { match: ue(/\\/, le, /[0\\tnr"']/) },
        { match: ue(/\\/, le, /u\{[0-9a-fA-F]{1,8}\}/) },
      ],
    }),
    N = (le = "") => ({
      className: "subst",
      match: ue(/\\/, le, /[\t ]*(?:[\r\n]|\r\n)/),
    }),
    x = (le = "") => ({
      className: "subst",
      label: "interpol",
      begin: ue(/\\/, le, /\(/),
      end: /\)/,
    }),
    O = (le = "") => ({
      begin: ue(le, /"""/),
      end: ue(/"""/, le),
      contains: [_(le), N(le), x(le)],
    }),
    I = (le = "") => ({
      begin: ue(le, /"/),
      end: ue(/"/, le),
      contains: [_(le), x(le)],
    }),
    U = {
      className: "string",
      variants: [
        O(),
        O("#"),
        O("##"),
        O("###"),
        I(),
        I("#"),
        I("##"),
        I("###"),
      ],
    },
    S = [
      e.BACKSLASH_ESCAPE,
      { begin: /\[/, end: /\]/, relevance: 0, contains: [e.BACKSLASH_ESCAPE] },
    ],
    F = { begin: /\/[^\s](?=[^/\n]*\/)/, end: /\//, contains: S },
    L = (le) => {
      const vt = ue(le, /\//),
        Y = ue(/\//, le);
      return {
        begin: vt,
        end: Y,
        contains: [...S, { scope: "comment", begin: `#(?!.*${Y})`, end: /$/ }],
      };
    },
    Q = { scope: "regexp", variants: [L("###"), L("##"), L("#"), F] },
    V = { match: ue(/`/, Mt, /`/) },
    G = { className: "variable", match: /\$\d+/ },
    R = { className: "variable", match: `\\$${Cl}+` },
    B = [V, G, R],
    C = {
      match: /(@|#(un)?)available/,
      scope: "keyword",
      starts: {
        contains: [
          { begin: /\(/, end: /\)/, keywords: aT, contains: [...E, b, U] },
        ],
      },
    },
    M = { scope: "keyword", match: ue(/@/, je(...lT), di(je(/\(/, /\s+/))) },
    v = { scope: "meta", match: ue(/@/, Mt) },
    H = [C, M, v],
    K = {
      match: di(/\b[A-Z]/),
      relevance: 0,
      contains: [
        {
          className: "type",
          match: ue(
            /(AV|CA|CF|CG|CI|CL|CM|CN|CT|MK|MP|MTK|MTL|NS|SCN|SK|UI|WK|XC)/,
            Cl,
            "+",
          ),
        },
        { className: "type", match: Lo, relevance: 0 },
        { match: /[?!]+/, relevance: 0 },
        { match: /\.\.\./, relevance: 0 },
        { match: ue(/\s+&\s+/, di(Lo)), relevance: 0 },
      ],
    },
    w = {
      begin: /</,
      end: />/,
      keywords: u,
      contains: [...r, ...d, ...H, g, K],
    };
  K.contains.push(w);
  const ne = { match: ue(Mt, /\s*:/), keywords: "_|0", relevance: 0 },
    pe = {
      begin: /\(/,
      end: /\)/,
      relevance: 0,
      keywords: u,
      contains: ["self", ne, ...r, Q, ...d, ...p, ...E, b, U, ...B, ...H, K],
    },
    oe = { begin: /</, end: />/, keywords: "repeat each", contains: [...r, K] },
    $e = {
      begin: je(di(ue(Mt, /\s*:/)), di(ue(Mt, /\s+/, Mt, /\s*:/))),
      end: /:/,
      relevance: 0,
      contains: [
        { className: "keyword", match: /\b_\b/ },
        { className: "params", match: Mt },
      ],
    },
    Ye = {
      begin: /\(/,
      end: /\)/,
      keywords: u,
      contains: [$e, ...r, ...d, ...E, b, U, ...H, K, pe],
      endsParent: !0,
      illegal: /["']/,
    },
    Rt = {
      match: [/(func|macro)/, /\s+/, je(V.match, Mt, Ga)],
      className: { 1: "keyword", 3: "title.function" },
      contains: [oe, Ye, t],
      illegal: [/\[/, /%/],
    },
    Ot = {
      match: [/\b(?:subscript|init[?!]?)/, /\s*(?=[<(])/],
      className: { 1: "keyword" },
      contains: [oe, Ye, t],
      illegal: /\[|%/,
    },
    nn = {
      match: [/operator/, /\s+/, Ga],
      className: { 1: "keyword", 3: "title" },
    },
    qr = {
      begin: [/precedencegroup/, /\s+/, Lo],
      className: { 1: "keyword", 3: "title" },
      contains: [K],
      keywords: [...iT, ...Jf],
      end: /}/,
    },
    rn = {
      match: [/class\b/, /\s+/, /func\b/, /\s+/, /\b[A-Za-z_][A-Za-z0-9_]*\b/],
      scope: { 1: "keyword", 3: "keyword", 5: "title.function" },
    },
    ir = {
      match: [/class\b/, /\s+/, /var\b/],
      scope: { 1: "keyword", 3: "keyword" },
    },
    He = {
      begin: [/(struct|protocol|class|extension|enum|actor)/, /\s+/, Mt, /\s*/],
      beginScope: { 1: "keyword", 3: "title.class" },
      keywords: u,
      contains: [
        oe,
        ...d,
        {
          begin: /:/,
          end: /\{/,
          keywords: u,
          contains: [{ scope: "title.class.inherited", match: Lo }, ...d],
          relevance: 0,
        },
      ],
    };
  for (const le of U.variants) {
    const vt = le.contains.find((In) => In.label === "interpol");
    vt.keywords = u;
    const Y = [...d, ...p, ...E, b, U, ...B];
    vt.contains = [...Y, { begin: /\(/, end: /\)/, contains: ["self", ...Y] }];
  }
  return {
    name: "Swift",
    keywords: u,
    contains: [
      ...r,
      Rt,
      Ot,
      rn,
      ir,
      He,
      nn,
      qr,
      { beginKeywords: "import", end: /$/, contains: [...r], relevance: 0 },
      Q,
      ...d,
      ...p,
      ...E,
      b,
      U,
      ...B,
      ...H,
      K,
      pe,
    ],
  };
}
const Tl = "[A-Za-z$_][0-9A-Za-z$_]*",
  cy = [
    "as",
    "in",
    "of",
    "if",
    "for",
    "while",
    "finally",
    "var",
    "new",
    "function",
    "do",
    "return",
    "void",
    "else",
    "break",
    "catch",
    "instanceof",
    "with",
    "throw",
    "case",
    "default",
    "try",
    "switch",
    "continue",
    "typeof",
    "delete",
    "let",
    "yield",
    "const",
    "class",
    "debugger",
    "async",
    "await",
    "static",
    "import",
    "from",
    "export",
    "extends",
    "using",
  ],
  dy = ["true", "false", "null", "undefined", "NaN", "Infinity"],
  fy = [
    "Object",
    "Function",
    "Boolean",
    "Symbol",
    "Math",
    "Date",
    "Number",
    "BigInt",
    "String",
    "RegExp",
    "Array",
    "Float32Array",
    "Float64Array",
    "Int8Array",
    "Uint8Array",
    "Uint8ClampedArray",
    "Int16Array",
    "Int32Array",
    "Uint16Array",
    "Uint32Array",
    "BigInt64Array",
    "BigUint64Array",
    "Set",
    "Map",
    "WeakSet",
    "WeakMap",
    "ArrayBuffer",
    "SharedArrayBuffer",
    "Atomics",
    "DataView",
    "JSON",
    "Promise",
    "Generator",
    "GeneratorFunction",
    "AsyncFunction",
    "Reflect",
    "Proxy",
    "Intl",
    "WebAssembly",
  ],
  py = [
    "Error",
    "EvalError",
    "InternalError",
    "RangeError",
    "ReferenceError",
    "SyntaxError",
    "TypeError",
    "URIError",
  ],
  hy = [
    "setInterval",
    "setTimeout",
    "clearInterval",
    "clearTimeout",
    "require",
    "exports",
    "eval",
    "isFinite",
    "isNaN",
    "parseFloat",
    "parseInt",
    "decodeURI",
    "decodeURIComponent",
    "encodeURI",
    "encodeURIComponent",
    "escape",
    "unescape",
  ],
  gy = [
    "arguments",
    "this",
    "super",
    "console",
    "window",
    "document",
    "localStorage",
    "sessionStorage",
    "module",
    "global",
  ],
  my = [].concat(hy, fy, py);
function uT(e) {
  const t = e.regex,
    n = (C, { after: M }) => {
      const v = "</" + C[0].slice(1);
      return C.input.indexOf(v, M) !== -1;
    },
    r = Tl,
    i = { begin: "<>", end: "</>" },
    o = /<[A-Za-z0-9\\._:-]+\s*\/>/,
    l = {
      begin: /<[A-Za-z0-9\\._:-]+/,
      end: /\/[A-Za-z0-9\\._:-]+>|\/>/,
      isTrulyOpeningTag: (C, M) => {
        const v = C[0].length + C.index,
          H = C.input[v];
        if (H === "<" || H === ",") {
          M.ignoreMatch();
          return;
        }
        H === ">" && (n(C, { after: v }) || M.ignoreMatch());
        let K;
        const w = C.input.substring(v);
        if ((K = w.match(/^\s*=/))) {
          M.ignoreMatch();
          return;
        }
        if ((K = w.match(/^\s+extends\s+/)) && K.index === 0) {
          M.ignoreMatch();
          return;
        }
      },
    },
    a = {
      $pattern: Tl,
      keyword: cy,
      literal: dy,
      built_in: my,
      "variable.language": gy,
    },
    s = "[0-9](_?[0-9])*",
    u = `\\.(${s})`,
    d = "0|[1-9](_?[0-9])*|0[0-7]*[89][0-9]*",
    c = {
      className: "number",
      variants: [
        { begin: `(\\b(${d})((${u})|\\.)?|(${u}))[eE][+-]?(${s})\\b` },
        { begin: `\\b(${d})\\b((${u})\\b|\\.)?|(${u})\\b` },
        { begin: "\\b(0|[1-9](_?[0-9])*)n\\b" },
        { begin: "\\b0[xX][0-9a-fA-F](_?[0-9a-fA-F])*n?\\b" },
        { begin: "\\b0[bB][0-1](_?[0-1])*n?\\b" },
        { begin: "\\b0[oO][0-7](_?[0-7])*n?\\b" },
        { begin: "\\b0[0-7]+n?\\b" },
      ],
      relevance: 0,
    },
    f = {
      className: "subst",
      begin: "\\$\\{",
      end: "\\}",
      keywords: a,
      contains: [],
    },
    p = {
      begin: ".?html`",
      end: "",
      starts: {
        end: "`",
        returnEnd: !1,
        contains: [e.BACKSLASH_ESCAPE, f],
        subLanguage: "xml",
      },
    },
    g = {
      begin: ".?css`",
      end: "",
      starts: {
        end: "`",
        returnEnd: !1,
        contains: [e.BACKSLASH_ESCAPE, f],
        subLanguage: "css",
      },
    },
    y = {
      begin: ".?gql`",
      end: "",
      starts: {
        end: "`",
        returnEnd: !1,
        contains: [e.BACKSLASH_ESCAPE, f],
        subLanguage: "graphql",
      },
    },
    E = {
      className: "string",
      begin: "`",
      end: "`",
      contains: [e.BACKSLASH_ESCAPE, f],
    },
    m = {
      className: "comment",
      variants: [
        e.COMMENT(/\/\*\*(?!\/)/, "\\*/", {
          relevance: 0,
          contains: [
            {
              begin: "(?=@[A-Za-z]+)",
              relevance: 0,
              contains: [
                { className: "doctag", begin: "@[A-Za-z]+" },
                {
                  className: "type",
                  begin: "\\{",
                  end: "\\}",
                  excludeEnd: !0,
                  excludeBegin: !0,
                  relevance: 0,
                },
                {
                  className: "variable",
                  begin: r + "(?=\\s*(-)|$)",
                  endsParent: !0,
                  relevance: 0,
                },
                { begin: /(?=[^\n])\s/, relevance: 0 },
              ],
            },
          ],
        }),
        e.C_BLOCK_COMMENT_MODE,
        e.C_LINE_COMMENT_MODE,
      ],
    },
    b = [
      e.APOS_STRING_MODE,
      e.QUOTE_STRING_MODE,
      p,
      g,
      y,
      E,
      { match: /\$\d+/ },
      c,
    ];
  f.contains = b.concat({
    begin: /\{/,
    end: /\}/,
    keywords: a,
    contains: ["self"].concat(b),
  });
  const _ = [].concat(m, f.contains),
    N = _.concat([
      {
        begin: /(\s*)\(/,
        end: /\)/,
        keywords: a,
        contains: ["self"].concat(_),
      },
    ]),
    x = {
      className: "params",
      begin: /(\s*)\(/,
      end: /\)/,
      excludeBegin: !0,
      excludeEnd: !0,
      keywords: a,
      contains: N,
    },
    O = {
      variants: [
        {
          match: [
            /class/,
            /\s+/,
            r,
            /\s+/,
            /extends/,
            /\s+/,
            t.concat(r, "(", t.concat(/\./, r), ")*"),
          ],
          scope: {
            1: "keyword",
            3: "title.class",
            5: "keyword",
            7: "title.class.inherited",
          },
        },
        {
          match: [/class/, /\s+/, r],
          scope: { 1: "keyword", 3: "title.class" },
        },
      ],
    },
    I = {
      relevance: 0,
      match: t.either(
        /\bJSON/,
        /\b[A-Z][a-z]+([A-Z][a-z]*|\d)*/,
        /\b[A-Z]{2,}([A-Z][a-z]+|\d)+([A-Z][a-z]*)*/,
        /\b[A-Z]{2,}[a-z]+([A-Z][a-z]+|\d)*([A-Z][a-z]*)*/,
      ),
      className: "title.class",
      keywords: { _: [...fy, ...py] },
    },
    U = {
      label: "use_strict",
      className: "meta",
      relevance: 10,
      begin: /^\s*['"]use (strict|asm)['"]/,
    },
    S = {
      variants: [
        { match: [/function/, /\s+/, r, /(?=\s*\()/] },
        { match: [/function/, /\s*(?=\()/] },
      ],
      className: { 1: "keyword", 3: "title.function" },
      label: "func.def",
      contains: [x],
      illegal: /%/,
    },
    F = {
      relevance: 0,
      match: /\b[A-Z][A-Z_0-9]+\b/,
      className: "variable.constant",
    };
  function L(C) {
    return t.concat("(?!", C.join("|"), ")");
  }
  const Q = {
      match: t.concat(
        /\b/,
        L([...hy, "super", "import"].map((C) => `${C}\\s*\\(`)),
        r,
        t.lookahead(/\s*\(/),
      ),
      className: "title.function",
      relevance: 0,
    },
    V = {
      begin: t.concat(/\./, t.lookahead(t.concat(r, /(?![0-9A-Za-z$_(])/))),
      end: r,
      excludeBegin: !0,
      keywords: "prototype",
      className: "property",
      relevance: 0,
    },
    G = {
      match: [/get|set/, /\s+/, r, /(?=\()/],
      className: { 1: "keyword", 3: "title.function" },
      contains: [{ begin: /\(\)/ }, x],
    },
    R =
      "(\\([^()]*(\\([^()]*(\\([^()]*\\)[^()]*)*\\)[^()]*)*\\)|" +
      e.UNDERSCORE_IDENT_RE +
      ")\\s*=>",
    B = {
      match: [
        /const|var|let/,
        /\s+/,
        r,
        /\s*/,
        /=\s*/,
        /(async\s*)?/,
        t.lookahead(R),
      ],
      keywords: "async",
      className: { 1: "keyword", 3: "title.function" },
      contains: [x],
    };
  return {
    name: "JavaScript",
    aliases: ["js", "jsx", "mjs", "cjs"],
    keywords: a,
    exports: { PARAMS_CONTAINS: N, CLASS_REFERENCE: I },
    illegal: /#(?![$_A-z])/,
    contains: [
      e.SHEBANG({ label: "shebang", binary: "node", relevance: 5 }),
      U,
      e.APOS_STRING_MODE,
      e.QUOTE_STRING_MODE,
      p,
      g,
      y,
      E,
      m,
      { match: /\$\d+/ },
      c,
      I,
      { scope: "attr", match: r + t.lookahead(":"), relevance: 0 },
      B,
      {
        begin: "(" + e.RE_STARTERS_RE + "|\\b(case|return|throw)\\b)\\s*",
        keywords: "return throw case",
        relevance: 0,
        contains: [
          m,
          e.REGEXP_MODE,
          {
            className: "function",
            begin: R,
            returnBegin: !0,
            end: "\\s*=>",
            contains: [
              {
                className: "params",
                variants: [
                  { begin: e.UNDERSCORE_IDENT_RE, relevance: 0 },
                  { className: null, begin: /\(\s*\)/, skip: !0 },
                  {
                    begin: /(\s*)\(/,
                    end: /\)/,
                    excludeBegin: !0,
                    excludeEnd: !0,
                    keywords: a,
                    contains: N,
                  },
                ],
              },
            ],
          },
          { begin: /,/, relevance: 0 },
          { match: /\s+/, relevance: 0 },
          {
            variants: [
              { begin: i.begin, end: i.end },
              { match: o },
              { begin: l.begin, "on:begin": l.isTrulyOpeningTag, end: l.end },
            ],
            subLanguage: "xml",
            contains: [
              { begin: l.begin, end: l.end, skip: !0, contains: ["self"] },
            ],
          },
        ],
      },
      S,
      { beginKeywords: "while if switch catch for" },
      {
        begin:
          "\\b(?!function)" +
          e.UNDERSCORE_IDENT_RE +
          "\\([^()]*(\\([^()]*(\\([^()]*\\)[^()]*)*\\)[^()]*)*\\)\\s*\\{",
        returnBegin: !0,
        label: "func.def",
        contains: [
          x,
          e.inherit(e.TITLE_MODE, { begin: r, className: "title.function" }),
        ],
      },
      { match: /\.\.\./, relevance: 0 },
      V,
      { match: "\\$" + r, relevance: 0 },
      {
        match: [/\bconstructor(?=\s*\()/],
        className: { 1: "title.function" },
        contains: [x],
      },
      Q,
      F,
      O,
      G,
      { match: /\$[(.]/ },
    ],
  };
}
function cT(e) {
  const t = e.regex,
    n = uT(e),
    r = Tl,
    i = [
      "any",
      "void",
      "number",
      "boolean",
      "string",
      "object",
      "never",
      "symbol",
      "bigint",
      "unknown",
    ],
    o = {
      begin: [/namespace/, /\s+/, e.IDENT_RE],
      beginScope: { 1: "keyword", 3: "title.class" },
    },
    l = {
      beginKeywords: "interface",
      end: /\{/,
      excludeEnd: !0,
      keywords: { keyword: "interface extends", built_in: i },
      contains: [n.exports.CLASS_REFERENCE],
    },
    a = { className: "meta", relevance: 10, begin: /^\s*['"]use strict['"]/ },
    s = [
      "type",
      "interface",
      "public",
      "private",
      "protected",
      "implements",
      "declare",
      "abstract",
      "readonly",
      "enum",
      "override",
      "satisfies",
    ],
    u = {
      $pattern: Tl,
      keyword: cy.concat(s),
      literal: dy,
      built_in: my.concat(i),
      "variable.language": gy,
    },
    d = { className: "meta", begin: "@" + r },
    c = (y, E, h) => {
      const m = y.contains.findIndex((b) => b.label === E);
      if (m === -1) throw new Error("can not find mode to replace");
      y.contains.splice(m, 1, h);
    };
  (Object.assign(n.keywords, u), n.exports.PARAMS_CONTAINS.push(d));
  const f = n.contains.find((y) => y.scope === "attr"),
    p = Object.assign({}, f, { match: t.concat(r, t.lookahead(/\s*\?:/)) });
  (n.exports.PARAMS_CONTAINS.push([n.exports.CLASS_REFERENCE, f, p]),
    (n.contains = n.contains.concat([d, o, l, p])),
    c(n, "shebang", e.SHEBANG()),
    c(n, "use_strict", a));
  const g = n.contains.find((y) => y.label === "func.def");
  return (
    (g.relevance = 0),
    Object.assign(n, {
      name: "TypeScript",
      aliases: ["ts", "tsx", "mts", "cts"],
    }),
    n
  );
}
function dT(e) {
  const t = e.regex,
    n = { className: "string", begin: /"(""|[^/n])"C\b/ },
    r = {
      className: "string",
      begin: /"/,
      end: /"/,
      illegal: /\n/,
      contains: [{ begin: /""/ }],
    },
    i = /\d{1,2}\/\d{1,2}\/\d{4}/,
    o = /\d{4}-\d{1,2}-\d{1,2}/,
    l = /(\d|1[012])(:\d+){0,2} *(AM|PM)/,
    a = /\d{1,2}(:\d{1,2}){1,2}/,
    s = {
      className: "literal",
      variants: [
        { begin: t.concat(/# */, t.either(o, i), / *#/) },
        { begin: t.concat(/# */, a, / *#/) },
        { begin: t.concat(/# */, l, / *#/) },
        { begin: t.concat(/# */, t.either(o, i), / +/, t.either(l, a), / *#/) },
      ],
    },
    u = {
      className: "number",
      relevance: 0,
      variants: [
        {
          begin:
            /\b\d[\d_]*((\.[\d_]+(E[+-]?[\d_]+)?)|(E[+-]?[\d_]+))[RFD@!#]?/,
        },
        { begin: /\b\d[\d_]*((U?[SIL])|[%&])?/ },
        { begin: /&H[\dA-F_]+((U?[SIL])|[%&])?/ },
        { begin: /&O[0-7_]+((U?[SIL])|[%&])?/ },
        { begin: /&B[01_]+((U?[SIL])|[%&])?/ },
      ],
    },
    d = { className: "label", begin: /^\w+:/ },
    c = e.COMMENT(/'''/, /$/, {
      contains: [{ className: "doctag", begin: /<\/?/, end: />/ }],
    }),
    f = e.COMMENT(null, /$/, {
      variants: [{ begin: /'/ }, { begin: /([\t ]|^)REM(?=\s)/ }],
    });
  return {
    name: "Visual Basic .NET",
    aliases: ["vb"],
    case_insensitive: !0,
    classNameAliases: { label: "symbol" },
    keywords: {
      keyword:
        "addhandler alias aggregate ansi as async assembly auto binary by byref byval call case catch class compare const continue custom declare default delegate dim distinct do each equals else elseif end enum erase error event exit explicit finally for friend from function get global goto group handles if implements imports in inherits interface into iterator join key let lib loop me mid module mustinherit mustoverride mybase myclass namespace narrowing new next notinheritable notoverridable of off on operator option optional order overloads overridable overrides paramarray partial preserve private property protected public raiseevent readonly redim removehandler resume return select set shadows shared skip static step stop structure strict sub synclock take text then throw to try unicode until using when where while widening with withevents writeonly yield",
      built_in:
        "addressof and andalso await directcast gettype getxmlnamespace is isfalse isnot istrue like mod nameof new not or orelse trycast typeof xor cbool cbyte cchar cdate cdbl cdec cint clng cobj csbyte cshort csng cstr cuint culng cushort",
      type: "boolean byte char date decimal double integer long object sbyte short single string uinteger ulong ushort",
      literal: "true false nothing",
    },
    illegal: "//|\\{|\\}|endif|gosub|variant|wend|^\\$ ",
    contains: [
      n,
      r,
      s,
      u,
      d,
      c,
      f,
      {
        className: "meta",
        begin:
          /[\t ]*#(const|disable|else|elseif|enable|end|externalsource|if|region)\b/,
        end: /$/,
        keywords: {
          keyword:
            "const disable else elseif enable end externalsource if region then",
        },
        contains: [f],
      },
    ],
  };
}
function fT(e) {
  e.regex;
  const t = e.COMMENT(/\(;/, /;\)/);
  t.contains.push("self");
  const n = e.COMMENT(/;;/, /$/),
    r = [
      "anyfunc",
      "block",
      "br",
      "br_if",
      "br_table",
      "call",
      "call_indirect",
      "data",
      "drop",
      "elem",
      "else",
      "end",
      "export",
      "func",
      "global.get",
      "global.set",
      "local.get",
      "local.set",
      "local.tee",
      "get_global",
      "get_local",
      "global",
      "if",
      "import",
      "local",
      "loop",
      "memory",
      "memory.grow",
      "memory.size",
      "module",
      "mut",
      "nop",
      "offset",
      "param",
      "result",
      "return",
      "select",
      "set_global",
      "set_local",
      "start",
      "table",
      "tee_local",
      "then",
      "type",
      "unreachable",
    ],
    i = {
      begin: [/(?:func|call|call_indirect)/, /\s+/, /\$[^\s)]+/],
      className: { 1: "keyword", 3: "title.function" },
    },
    o = { className: "variable", begin: /\$[\w_]+/ },
    l = { match: /(\((?!;)|\))+/, className: "punctuation", relevance: 0 },
    a = {
      className: "number",
      relevance: 0,
      match:
        /[+-]?\b(?:\d(?:_?\d)*(?:\.\d(?:_?\d)*)?(?:[eE][+-]?\d(?:_?\d)*)?|0x[\da-fA-F](?:_?[\da-fA-F])*(?:\.[\da-fA-F](?:_?[\da-fA-D])*)?(?:[pP][+-]?\d(?:_?\d)*)?)\b|\binf\b|\bnan(?::0x[\da-fA-F](?:_?[\da-fA-D])*)?\b/,
    },
    s = { match: /(i32|i64|f32|f64)(?!\.)/, className: "type" },
    u = {
      className: "keyword",
      match:
        /\b(f32|f64|i32|i64)(?:\.(?:abs|add|and|ceil|clz|const|convert_[su]\/i(?:32|64)|copysign|ctz|demote\/f64|div(?:_[su])?|eqz?|extend_[su]\/i32|floor|ge(?:_[su])?|gt(?:_[su])?|le(?:_[su])?|load(?:(?:8|16|32)_[su])?|lt(?:_[su])?|max|min|mul|nearest|neg?|or|popcnt|promote\/f32|reinterpret\/[fi](?:32|64)|rem_[su]|rot[lr]|shl|shr_[su]|store(?:8|16|32)?|sqrt|sub|trunc(?:_[su]\/f(?:32|64))?|wrap\/i64|xor))\b/,
    };
  return {
    name: "WebAssembly",
    keywords: { $pattern: /[\w.]+/, keyword: r },
    contains: [
      n,
      t,
      {
        match: [/(?:offset|align)/, /\s*/, /=/],
        className: { 1: "keyword", 3: "operator" },
      },
      o,
      l,
      i,
      e.QUOTE_STRING_MODE,
      s,
      u,
      a,
    ],
  };
}
function pT(e) {
  const t = e.regex,
    n = t.concat(
      /[\p{L}_]/u,
      t.optional(/[\p{L}0-9_.-]*:/u),
      /[\p{L}0-9_.-]*/u,
    ),
    r = /[\p{L}0-9._:-]+/u,
    i = { className: "symbol", begin: /&[a-z]+;|&#[0-9]+;|&#x[a-f0-9]+;/ },
    o = {
      begin: /\s/,
      contains: [
        { className: "keyword", begin: /#?[a-z_][a-z1-9_-]+/, illegal: /\n/ },
      ],
    },
    l = e.inherit(o, { begin: /\(/, end: /\)/ }),
    a = e.inherit(e.APOS_STRING_MODE, { className: "string" }),
    s = e.inherit(e.QUOTE_STRING_MODE, { className: "string" }),
    u = {
      endsWithParent: !0,
      illegal: /</,
      relevance: 0,
      contains: [
        { className: "attr", begin: r, relevance: 0 },
        {
          begin: /=\s*/,
          relevance: 0,
          contains: [
            {
              className: "string",
              endsParent: !0,
              variants: [
                { begin: /"/, end: /"/, contains: [i] },
                { begin: /'/, end: /'/, contains: [i] },
                { begin: /[^\s"'=<>`]+/ },
              ],
            },
          ],
        },
      ],
    };
  return {
    name: "HTML, XML",
    aliases: [
      "html",
      "xhtml",
      "rss",
      "atom",
      "xjb",
      "xsd",
      "xsl",
      "plist",
      "wsf",
      "svg",
    ],
    case_insensitive: !0,
    unicodeRegex: !0,
    contains: [
      {
        className: "meta",
        begin: /<![a-z]/,
        end: />/,
        relevance: 10,
        contains: [
          o,
          s,
          a,
          l,
          {
            begin: /\[/,
            end: /\]/,
            contains: [
              {
                className: "meta",
                begin: /<![a-z]/,
                end: />/,
                contains: [o, l, s, a],
              },
            ],
          },
        ],
      },
      e.COMMENT(/<!--/, /-->/, { relevance: 10 }),
      { begin: /<!\[CDATA\[/, end: /\]\]>/, relevance: 10 },
      i,
      {
        className: "meta",
        end: /\?>/,
        variants: [
          { begin: /<\?xml/, relevance: 10, contains: [s] },
          { begin: /<\?[a-z][a-z0-9]+/ },
        ],
      },
      {
        className: "tag",
        begin: /<style(?=\s|>)/,
        end: />/,
        keywords: { name: "style" },
        contains: [u],
        starts: {
          end: /<\/style>/,
          returnEnd: !0,
          subLanguage: ["css", "xml"],
        },
      },
      {
        className: "tag",
        begin: /<script(?=\s|>)/,
        end: />/,
        keywords: { name: "script" },
        contains: [u],
        starts: {
          end: /<\/script>/,
          returnEnd: !0,
          subLanguage: ["javascript", "handlebars", "xml"],
        },
      },
      { className: "tag", begin: /<>|<\/>/ },
      {
        className: "tag",
        begin: t.concat(
          /</,
          t.lookahead(t.concat(n, t.either(/\/>/, />/, /\s/))),
        ),
        end: /\/?>/,
        contains: [{ className: "name", begin: n, relevance: 0, starts: u }],
      },
      {
        className: "tag",
        begin: t.concat(/<\//, t.lookahead(t.concat(n, />/))),
        contains: [
          { className: "name", begin: n, relevance: 0 },
          { begin: />/, relevance: 0, endsParent: !0 },
        ],
      },
    ],
  };
}
function hT(e) {
  const t = "true false yes no null",
    n = "[\\w#;/?:@&=+$,.~*'()[\\]]+",
    r = {
      className: "attr",
      variants: [
        { begin: /[\w*@][\w*@ :()\./-]*:(?=[ \t]|$)/ },
        { begin: /"[\w*@][\w*@ :()\./-]*":(?=[ \t]|$)/ },
        { begin: /'[\w*@][\w*@ :()\./-]*':(?=[ \t]|$)/ },
      ],
    },
    i = {
      className: "template-variable",
      variants: [
        { begin: /\{\{/, end: /\}\}/ },
        { begin: /%\{/, end: /\}/ },
      ],
    },
    o = {
      className: "string",
      relevance: 0,
      begin: /'/,
      end: /'/,
      contains: [{ match: /''/, scope: "char.escape", relevance: 0 }],
    },
    l = {
      className: "string",
      relevance: 0,
      variants: [{ begin: /"/, end: /"/ }, { begin: /\S+/ }],
      contains: [e.BACKSLASH_ESCAPE, i],
    },
    a = e.inherit(l, {
      variants: [
        { begin: /'/, end: /'/, contains: [{ begin: /''/, relevance: 0 }] },
        { begin: /"/, end: /"/ },
        { begin: /[^\s,{}[\]]+/ },
      ],
    }),
    f = {
      className: "number",
      begin:
        "\\b" +
        "[0-9]{4}(-[0-9][0-9]){0,2}" +
        "([Tt \\t][0-9][0-9]?(:[0-9][0-9]){2})?" +
        "(\\.[0-9]*)?" +
        "([ \\t])*(Z|[-+][0-9][0-9]?(:[0-9][0-9])?)?" +
        "\\b",
    },
    p = {
      end: ",",
      endsWithParent: !0,
      excludeEnd: !0,
      keywords: t,
      relevance: 0,
    },
    g = { begin: /\{/, end: /\}/, contains: [p], illegal: "\\n", relevance: 0 },
    y = {
      begin: "\\[",
      end: "\\]",
      contains: [p],
      illegal: "\\n",
      relevance: 0,
    },
    E = [
      r,
      { className: "meta", begin: "^---\\s*$", relevance: 10 },
      {
        className: "string",
        begin: "[\\|>]([1-9]?[+-])?[ ]*\\n( +)[^ ][^\\n]*\\n(\\2[^\\n]+\\n?)*",
      },
      {
        begin: "<%[%=-]?",
        end: "[%-]?%>",
        subLanguage: "ruby",
        excludeBegin: !0,
        excludeEnd: !0,
        relevance: 0,
      },
      { className: "type", begin: "!\\w+!" + n },
      { className: "type", begin: "!<" + n + ">" },
      { className: "type", begin: "!" + n },
      { className: "type", begin: "!!" + n },
      { className: "meta", begin: "&" + e.UNDERSCORE_IDENT_RE + "$" },
      { className: "meta", begin: "\\*" + e.UNDERSCORE_IDENT_RE + "$" },
      { className: "bullet", begin: "-(?=[ ]|$)", relevance: 0 },
      e.HASH_COMMENT_MODE,
      { beginKeywords: t, keywords: { literal: t } },
      f,
      { className: "number", begin: e.C_NUMBER_RE + "\\b", relevance: 0 },
      g,
      y,
      o,
      l,
    ],
    h = [...E];
  return (
    h.pop(),
    h.push(a),
    (p.contains = h),
    { name: "YAML", case_insensitive: !0, aliases: ["yml"], contains: E }
  );
}
const gT = {
  arduino: QN,
  bash: ZN,
  c: XN,
  cpp: JN,
  csharp: eC,
  css: uC,
  diff: cC,
  go: dC,
  graphql: fC,
  ini: pC,
  java: hC,
  javascript: vC,
  json: EC,
  kotlin: xC,
  less: RC,
  lua: OC,
  makefile: IC,
  markdown: MC,
  objectivec: LC,
  perl: DC,
  php: PC,
  "php-template": zC,
  plaintext: FC,
  python: BC,
  "python-repl": UC,
  r: $C,
  ruby: HC,
  rust: jC,
  scss: XC,
  shell: JC,
  sql: eT,
  swift: sT,
  typescript: cT,
  vbnet: dT,
  wasm: fT,
  xml: pT,
  yaml: hT,
};
function yy(e) {
  return (
    e instanceof Map
      ? (e.clear =
          e.delete =
          e.set =
            function () {
              throw new Error("map is read-only");
            })
      : e instanceof Set &&
        (e.add =
          e.clear =
          e.delete =
            function () {
              throw new Error("set is read-only");
            }),
    Object.freeze(e),
    Object.getOwnPropertyNames(e).forEach((t) => {
      const n = e[t],
        r = typeof n;
      (r === "object" || r === "function") && !Object.isFrozen(n) && yy(n);
    }),
    e
  );
}
class tp {
  constructor(t) {
    (t.data === void 0 && (t.data = {}),
      (this.data = t.data),
      (this.isMatchIgnored = !1));
  }
  ignoreMatch() {
    this.isMatchIgnored = !0;
  }
}
function by(e) {
  return e
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#x27;");
}
function yn(e, ...t) {
  const n = Object.create(null);
  for (const r in e) n[r] = e[r];
  return (
    t.forEach(function (r) {
      for (const i in r) n[i] = r[i];
    }),
    n
  );
}
const mT = "</span>",
  np = (e) => !!e.scope,
  yT = (e, { prefix: t }) => {
    if (e.startsWith("language:")) return e.replace("language:", "language-");
    if (e.includes(".")) {
      const n = e.split(".");
      return [
        `${t}${n.shift()}`,
        ...n.map((r, i) => `${r}${"_".repeat(i + 1)}`),
      ].join(" ");
    }
    return `${t}${e}`;
  };
class bT {
  constructor(t, n) {
    ((this.buffer = ""), (this.classPrefix = n.classPrefix), t.walk(this));
  }
  addText(t) {
    this.buffer += by(t);
  }
  openNode(t) {
    if (!np(t)) return;
    const n = yT(t.scope, { prefix: this.classPrefix });
    this.span(n);
  }
  closeNode(t) {
    np(t) && (this.buffer += mT);
  }
  value() {
    return this.buffer;
  }
  span(t) {
    this.buffer += `<span class="${t}">`;
  }
}
const rp = (e = {}) => {
  const t = { children: [] };
  return (Object.assign(t, e), t);
};
class kc {
  constructor() {
    ((this.rootNode = rp()), (this.stack = [this.rootNode]));
  }
  get top() {
    return this.stack[this.stack.length - 1];
  }
  get root() {
    return this.rootNode;
  }
  add(t) {
    this.top.children.push(t);
  }
  openNode(t) {
    const n = rp({ scope: t });
    (this.add(n), this.stack.push(n));
  }
  closeNode() {
    if (this.stack.length > 1) return this.stack.pop();
  }
  closeAllNodes() {
    for (; this.closeNode(););
  }
  toJSON() {
    return JSON.stringify(this.rootNode, null, 4);
  }
  walk(t) {
    return this.constructor._walk(t, this.rootNode);
  }
  static _walk(t, n) {
    return (
      typeof n == "string"
        ? t.addText(n)
        : n.children &&
          (t.openNode(n),
          n.children.forEach((r) => this._walk(t, r)),
          t.closeNode(n)),
      t
    );
  }
  static _collapse(t) {
    typeof t != "string" &&
      t.children &&
      (t.children.every((n) => typeof n == "string")
        ? (t.children = [t.children.join("")])
        : t.children.forEach((n) => {
            kc._collapse(n);
          }));
  }
}
class vT extends kc {
  constructor(t) {
    (super(), (this.options = t));
  }
  addText(t) {
    t !== "" && this.add(t);
  }
  startScope(t) {
    this.openNode(t);
  }
  endScope() {
    this.closeNode();
  }
  __addSublanguage(t, n) {
    const r = t.root;
    (n && (r.scope = `language:${n}`), this.add(r));
  }
  toHTML() {
    return new bT(this, this.options).value();
  }
  finalize() {
    return (this.closeAllNodes(), !0);
  }
}
function Yi(e) {
  return e ? (typeof e == "string" ? e : e.source) : null;
}
function vy(e) {
  return rr("(?=", e, ")");
}
function ET(e) {
  return rr("(?:", e, ")*");
}
function wT(e) {
  return rr("(?:", e, ")?");
}
function rr(...e) {
  return e.map((n) => Yi(n)).join("");
}
function xT(e) {
  const t = e[e.length - 1];
  return typeof t == "object" && t.constructor === Object
    ? (e.splice(e.length - 1, 1), t)
    : {};
}
function Sc(...e) {
  return (
    "(" + (xT(e).capture ? "" : "?:") + e.map((r) => Yi(r)).join("|") + ")"
  );
}
function Ey(e) {
  return new RegExp(e.toString() + "|").exec("").length - 1;
}
function _T(e, t) {
  const n = e && e.exec(t);
  return n && n.index === 0;
}
const kT = /\[(?:[^\\\]]|\\.)*\]|\(\??|\\([1-9][0-9]*)|\\./;
function Nc(e, { joinWith: t }) {
  let n = 0;
  return e
    .map((r) => {
      n += 1;
      const i = n;
      let o = Yi(r),
        l = "";
      for (; o.length > 0;) {
        const a = kT.exec(o);
        if (!a) {
          l += o;
          break;
        }
        ((l += o.substring(0, a.index)),
          (o = o.substring(a.index + a[0].length)),
          a[0][0] === "\\" && a[1]
            ? (l += "\\" + String(Number(a[1]) + i))
            : ((l += a[0]), a[0] === "(" && n++));
      }
      return l;
    })
    .map((r) => `(${r})`)
    .join(t);
}
const ST = /\b\B/,
  wy = "[a-zA-Z]\\w*",
  Cc = "[a-zA-Z_]\\w*",
  xy = "\\b\\d+(\\.\\d+)?",
  _y = "(-?)(\\b0[xX][a-fA-F0-9]+|(\\b\\d+(\\.\\d*)?|\\.\\d+)([eE][-+]?\\d+)?)",
  ky = "\\b(0b[01]+)",
  NT =
    "!|!=|!==|%|%=|&|&&|&=|\\*|\\*=|\\+|\\+=|,|-|-=|/=|/|:|;|<<|<<=|<=|<|===|==|=|>>>=|>>=|>=|>>>|>>|>|\\?|\\[|\\{|\\(|\\^|\\^=|\\||\\|=|\\|\\||~",
  CT = (e = {}) => {
    const t = /^#![ ]*\//;
    return (
      e.binary && (e.begin = rr(t, /.*\b/, e.binary, /\b.*/)),
      yn(
        {
          scope: "meta",
          begin: t,
          end: /$/,
          relevance: 0,
          "on:begin": (n, r) => {
            n.index !== 0 && r.ignoreMatch();
          },
        },
        e,
      )
    );
  },
  Qi = { begin: "\\\\[\\s\\S]", relevance: 0 },
  TT = {
    scope: "string",
    begin: "'",
    end: "'",
    illegal: "\\n",
    contains: [Qi],
  },
  AT = {
    scope: "string",
    begin: '"',
    end: '"',
    illegal: "\\n",
    contains: [Qi],
  },
  RT = {
    begin:
      /\b(a|an|the|are|I'm|isn't|don't|doesn't|won't|but|just|should|pretty|simply|enough|gonna|going|wtf|so|such|will|you|your|they|like|more)\b/,
  },
  ea = function (e, t, n = {}) {
    const r = yn({ scope: "comment", begin: e, end: t, contains: [] }, n);
    r.contains.push({
      scope: "doctag",
      begin: "[ ]*(?=(TODO|FIXME|NOTE|BUG|OPTIMIZE|HACK|XXX):)",
      end: /(TODO|FIXME|NOTE|BUG|OPTIMIZE|HACK|XXX):/,
      excludeBegin: !0,
      relevance: 0,
    });
    const i = Sc(
      "I",
      "a",
      "is",
      "so",
      "us",
      "to",
      "at",
      "if",
      "in",
      "it",
      "on",
      /[A-Za-z]+['](d|ve|re|ll|t|s|n)/,
      /[A-Za-z]+[-][a-z]+/,
      /[A-Za-z][a-z]{2,}/,
    );
    return (
      r.contains.push({
        begin: rr(/[ ]+/, "(", i, /[.]?[:]?([.][ ]|[ ])/, "){3}"),
      }),
      r
    );
  },
  OT = ea("//", "$"),
  IT = ea("/\\*", "\\*/"),
  MT = ea("#", "$"),
  LT = { scope: "number", begin: xy, relevance: 0 },
  DT = { scope: "number", begin: _y, relevance: 0 },
  PT = { scope: "number", begin: ky, relevance: 0 },
  zT = {
    scope: "regexp",
    begin: /\/(?=[^/\n]*\/)/,
    end: /\/[gimuy]*/,
    contains: [Qi, { begin: /\[/, end: /\]/, relevance: 0, contains: [Qi] }],
  },
  FT = { scope: "title", begin: wy, relevance: 0 },
  BT = { scope: "title", begin: Cc, relevance: 0 },
  UT = { begin: "\\.\\s*" + Cc, relevance: 0 },
  $T = function (e) {
    return Object.assign(e, {
      "on:begin": (t, n) => {
        n.data._beginMatch = t[1];
      },
      "on:end": (t, n) => {
        n.data._beginMatch !== t[1] && n.ignoreMatch();
      },
    });
  };
var Do = Object.freeze({
  __proto__: null,
  APOS_STRING_MODE: TT,
  BACKSLASH_ESCAPE: Qi,
  BINARY_NUMBER_MODE: PT,
  BINARY_NUMBER_RE: ky,
  COMMENT: ea,
  C_BLOCK_COMMENT_MODE: IT,
  C_LINE_COMMENT_MODE: OT,
  C_NUMBER_MODE: DT,
  C_NUMBER_RE: _y,
  END_SAME_AS_BEGIN: $T,
  HASH_COMMENT_MODE: MT,
  IDENT_RE: wy,
  MATCH_NOTHING_RE: ST,
  METHOD_GUARD: UT,
  NUMBER_MODE: LT,
  NUMBER_RE: xy,
  PHRASAL_WORDS_MODE: RT,
  QUOTE_STRING_MODE: AT,
  REGEXP_MODE: zT,
  RE_STARTERS_RE: NT,
  SHEBANG: CT,
  TITLE_MODE: FT,
  UNDERSCORE_IDENT_RE: Cc,
  UNDERSCORE_TITLE_MODE: BT,
});
function HT(e, t) {
  e.input[e.index - 1] === "." && t.ignoreMatch();
}
function jT(e, t) {
  e.className !== void 0 && ((e.scope = e.className), delete e.className);
}
function WT(e, t) {
  t &&
    e.beginKeywords &&
    ((e.begin =
      "\\b(" + e.beginKeywords.split(" ").join("|") + ")(?!\\.)(?=\\b|\\s)"),
    (e.__beforeBegin = HT),
    (e.keywords = e.keywords || e.beginKeywords),
    delete e.beginKeywords,
    e.relevance === void 0 && (e.relevance = 0));
}
function GT(e, t) {
  Array.isArray(e.illegal) && (e.illegal = Sc(...e.illegal));
}
function KT(e, t) {
  if (e.match) {
    if (e.begin || e.end)
      throw new Error("begin & end are not supported with match");
    ((e.begin = e.match), delete e.match);
  }
}
function VT(e, t) {
  e.relevance === void 0 && (e.relevance = 1);
}
const qT = (e, t) => {
    if (!e.beforeMatch) return;
    if (e.starts) throw new Error("beforeMatch cannot be used with starts");
    const n = Object.assign({}, e);
    (Object.keys(e).forEach((r) => {
      delete e[r];
    }),
      (e.keywords = n.keywords),
      (e.begin = rr(n.beforeMatch, vy(n.begin))),
      (e.starts = {
        relevance: 0,
        contains: [Object.assign(n, { endsParent: !0 })],
      }),
      (e.relevance = 0),
      delete n.beforeMatch);
  },
  YT = [
    "of",
    "and",
    "for",
    "in",
    "not",
    "or",
    "if",
    "then",
    "parent",
    "list",
    "value",
  ],
  QT = "keyword";
function Sy(e, t, n = QT) {
  const r = Object.create(null);
  return (
    typeof e == "string"
      ? i(n, e.split(" "))
      : Array.isArray(e)
        ? i(n, e)
        : Object.keys(e).forEach(function (o) {
            Object.assign(r, Sy(e[o], t, o));
          }),
    r
  );
  function i(o, l) {
    (t && (l = l.map((a) => a.toLowerCase())),
      l.forEach(function (a) {
        const s = a.split("|");
        r[s[0]] = [o, ZT(s[0], s[1])];
      }));
  }
}
function ZT(e, t) {
  return t ? Number(t) : XT(e) ? 0 : 1;
}
function XT(e) {
  return YT.includes(e.toLowerCase());
}
const ip = {},
  Gn = (e) => {
    console.error(e);
  },
  op = (e, ...t) => {
    console.log(`WARN: ${e}`, ...t);
  },
  sr = (e, t) => {
    ip[`${e}/${t}`] ||
      (console.log(`Deprecated as of ${e}. ${t}`), (ip[`${e}/${t}`] = !0));
  },
  Al = new Error();
function Ny(e, t, { key: n }) {
  let r = 0;
  const i = e[n],
    o = {},
    l = {};
  for (let a = 1; a <= t.length; a++)
    ((l[a + r] = i[a]), (o[a + r] = !0), (r += Ey(t[a - 1])));
  ((e[n] = l), (e[n]._emit = o), (e[n]._multi = !0));
}
function JT(e) {
  if (Array.isArray(e.begin)) {
    if (e.skip || e.excludeBegin || e.returnBegin)
      throw (
        Gn(
          "skip, excludeBegin, returnBegin not compatible with beginScope: {}",
        ),
        Al
      );
    if (typeof e.beginScope != "object" || e.beginScope === null)
      throw (Gn("beginScope must be object"), Al);
    (Ny(e, e.begin, { key: "beginScope" }),
      (e.begin = Nc(e.begin, { joinWith: "" })));
  }
}
function eA(e) {
  if (Array.isArray(e.end)) {
    if (e.skip || e.excludeEnd || e.returnEnd)
      throw (
        Gn("skip, excludeEnd, returnEnd not compatible with endScope: {}"),
        Al
      );
    if (typeof e.endScope != "object" || e.endScope === null)
      throw (Gn("endScope must be object"), Al);
    (Ny(e, e.end, { key: "endScope" }), (e.end = Nc(e.end, { joinWith: "" })));
  }
}
function tA(e) {
  e.scope &&
    typeof e.scope == "object" &&
    e.scope !== null &&
    ((e.beginScope = e.scope), delete e.scope);
}
function nA(e) {
  (tA(e),
    typeof e.beginScope == "string" && (e.beginScope = { _wrap: e.beginScope }),
    typeof e.endScope == "string" && (e.endScope = { _wrap: e.endScope }),
    JT(e),
    eA(e));
}
function rA(e) {
  function t(l, a) {
    return new RegExp(
      Yi(l),
      "m" +
        (e.case_insensitive ? "i" : "") +
        (e.unicodeRegex ? "u" : "") +
        (a ? "g" : ""),
    );
  }
  class n {
    constructor() {
      ((this.matchIndexes = {}),
        (this.regexes = []),
        (this.matchAt = 1),
        (this.position = 0));
    }
    addRule(a, s) {
      ((s.position = this.position++),
        (this.matchIndexes[this.matchAt] = s),
        this.regexes.push([s, a]),
        (this.matchAt += Ey(a) + 1));
    }
    compile() {
      this.regexes.length === 0 && (this.exec = () => null);
      const a = this.regexes.map((s) => s[1]);
      ((this.matcherRe = t(Nc(a, { joinWith: "|" }), !0)),
        (this.lastIndex = 0));
    }
    exec(a) {
      this.matcherRe.lastIndex = this.lastIndex;
      const s = this.matcherRe.exec(a);
      if (!s) return null;
      const u = s.findIndex((c, f) => f > 0 && c !== void 0),
        d = this.matchIndexes[u];
      return (s.splice(0, u), Object.assign(s, d));
    }
  }
  class r {
    constructor() {
      ((this.rules = []),
        (this.multiRegexes = []),
        (this.count = 0),
        (this.lastIndex = 0),
        (this.regexIndex = 0));
    }
    getMatcher(a) {
      if (this.multiRegexes[a]) return this.multiRegexes[a];
      const s = new n();
      return (
        this.rules.slice(a).forEach(([u, d]) => s.addRule(u, d)),
        s.compile(),
        (this.multiRegexes[a] = s),
        s
      );
    }
    resumingScanAtSamePosition() {
      return this.regexIndex !== 0;
    }
    considerAll() {
      this.regexIndex = 0;
    }
    addRule(a, s) {
      (this.rules.push([a, s]), s.type === "begin" && this.count++);
    }
    exec(a) {
      const s = this.getMatcher(this.regexIndex);
      s.lastIndex = this.lastIndex;
      let u = s.exec(a);
      if (
        this.resumingScanAtSamePosition() &&
        !(u && u.index === this.lastIndex)
      ) {
        const d = this.getMatcher(0);
        ((d.lastIndex = this.lastIndex + 1), (u = d.exec(a)));
      }
      return (
        u &&
          ((this.regexIndex += u.position + 1),
          this.regexIndex === this.count && this.considerAll()),
        u
      );
    }
  }
  function i(l) {
    const a = new r();
    return (
      l.contains.forEach((s) => a.addRule(s.begin, { rule: s, type: "begin" })),
      l.terminatorEnd && a.addRule(l.terminatorEnd, { type: "end" }),
      l.illegal && a.addRule(l.illegal, { type: "illegal" }),
      a
    );
  }
  function o(l, a) {
    const s = l;
    if (l.isCompiled) return s;
    ([jT, KT, nA, qT].forEach((d) => d(l, a)),
      e.compilerExtensions.forEach((d) => d(l, a)),
      (l.__beforeBegin = null),
      [WT, GT, VT].forEach((d) => d(l, a)),
      (l.isCompiled = !0));
    let u = null;
    return (
      typeof l.keywords == "object" &&
        l.keywords.$pattern &&
        ((l.keywords = Object.assign({}, l.keywords)),
        (u = l.keywords.$pattern),
        delete l.keywords.$pattern),
      (u = u || /\w+/),
      l.keywords && (l.keywords = Sy(l.keywords, e.case_insensitive)),
      (s.keywordPatternRe = t(u, !0)),
      a &&
        (l.begin || (l.begin = /\B|\b/),
        (s.beginRe = t(s.begin)),
        !l.end && !l.endsWithParent && (l.end = /\B|\b/),
        l.end && (s.endRe = t(s.end)),
        (s.terminatorEnd = Yi(s.end) || ""),
        l.endsWithParent &&
          a.terminatorEnd &&
          (s.terminatorEnd += (l.end ? "|" : "") + a.terminatorEnd)),
      l.illegal && (s.illegalRe = t(l.illegal)),
      l.contains || (l.contains = []),
      (l.contains = [].concat(
        ...l.contains.map(function (d) {
          return iA(d === "self" ? l : d);
        }),
      )),
      l.contains.forEach(function (d) {
        o(d, s);
      }),
      l.starts && o(l.starts, a),
      (s.matcher = i(s)),
      s
    );
  }
  if (
    (e.compilerExtensions || (e.compilerExtensions = []),
    e.contains && e.contains.includes("self"))
  )
    throw new Error(
      "ERR: contains `self` is not supported at the top-level of a language.  See documentation.",
    );
  return ((e.classNameAliases = yn(e.classNameAliases || {})), o(e));
}
function Cy(e) {
  return e ? e.endsWithParent || Cy(e.starts) : !1;
}
function iA(e) {
  return (
    e.variants &&
      !e.cachedVariants &&
      (e.cachedVariants = e.variants.map(function (t) {
        return yn(e, { variants: null }, t);
      })),
    e.cachedVariants
      ? e.cachedVariants
      : Cy(e)
        ? yn(e, { starts: e.starts ? yn(e.starts) : null })
        : Object.isFrozen(e)
          ? yn(e)
          : e
  );
}
var oA = "11.11.1";
class lA extends Error {
  constructor(t, n) {
    (super(t), (this.name = "HTMLInjectionError"), (this.html = n));
  }
}
const Ka = by,
  lp = yn,
  ap = Symbol("nomatch"),
  aA = 7,
  Ty = function (e) {
    const t = Object.create(null),
      n = Object.create(null),
      r = [];
    let i = !0;
    const o =
        "Could not find the language '{}', did you forget to load/include a language module?",
      l = { disableAutodetect: !0, name: "Plain text", contains: [] };
    let a = {
      ignoreUnescapedHTML: !1,
      throwUnescapedHTML: !1,
      noHighlightRe: /^(no-?highlight)$/i,
      languageDetectRe: /\blang(?:uage)?-([\w-]+)\b/i,
      classPrefix: "hljs-",
      cssSelector: "pre code",
      languages: null,
      __emitter: vT,
    };
    function s(R) {
      return a.noHighlightRe.test(R);
    }
    function u(R) {
      let B = R.className + " ";
      B += R.parentNode ? R.parentNode.className : "";
      const C = a.languageDetectRe.exec(B);
      if (C) {
        const M = I(C[1]);
        return (
          M ||
            (op(o.replace("{}", C[1])),
            op("Falling back to no-highlight mode for this block.", R)),
          M ? C[1] : "no-highlight"
        );
      }
      return B.split(/\s+/).find((M) => s(M) || I(M));
    }
    function d(R, B, C) {
      let M = "",
        v = "";
      (typeof B == "object"
        ? ((M = R), (C = B.ignoreIllegals), (v = B.language))
        : (sr("10.7.0", "highlight(lang, code, ...args) has been deprecated."),
          sr(
            "10.7.0",
            `Please use highlight(code, options) instead.
https://github.com/highlightjs/highlight.js/issues/2277`,
          ),
          (v = R),
          (M = B)),
        C === void 0 && (C = !0));
      const H = { code: M, language: v };
      V("before:highlight", H);
      const K = H.result ? H.result : c(H.language, H.code, C);
      return ((K.code = H.code), V("after:highlight", K), K);
    }
    function c(R, B, C, M) {
      const v = Object.create(null);
      function H(k, A) {
        return k.keywords[A];
      }
      function K() {
        if (!Y.keywords) {
          ke.addText(se);
          return;
        }
        let k = 0;
        Y.keywordPatternRe.lastIndex = 0;
        let A = Y.keywordPatternRe.exec(se),
          $ = "";
        for (; A;) {
          $ += se.substring(k, A.index);
          const W = He.case_insensitive ? A[0].toLowerCase() : A[0],
            X = H(Y, W);
          if (X) {
            const [xe, $t] = X;
            if (
              (ke.addText($),
              ($ = ""),
              (v[W] = (v[W] || 0) + 1),
              v[W] <= aA && (or += $t),
              xe.startsWith("_"))
            )
              $ += A[0];
            else {
              const Et = He.classNameAliases[xe] || xe;
              pe(A[0], Et);
            }
          } else $ += A[0];
          ((k = Y.keywordPatternRe.lastIndex),
            (A = Y.keywordPatternRe.exec(se)));
        }
        (($ += se.substring(k)), ke.addText($));
      }
      function w() {
        if (se === "") return;
        let k = null;
        if (typeof Y.subLanguage == "string") {
          if (!t[Y.subLanguage]) {
            ke.addText(se);
            return;
          }
          ((k = c(Y.subLanguage, se, !0, In[Y.subLanguage])),
            (In[Y.subLanguage] = k._top));
        } else k = p(se, Y.subLanguage.length ? Y.subLanguage : null);
        (Y.relevance > 0 && (or += k.relevance),
          ke.__addSublanguage(k._emitter, k.language));
      }
      function ne() {
        (Y.subLanguage != null ? w() : K(), (se = ""));
      }
      function pe(k, A) {
        k !== "" && (ke.startScope(A), ke.addText(k), ke.endScope());
      }
      function oe(k, A) {
        let $ = 1;
        const W = A.length - 1;
        for (; $ <= W;) {
          if (!k._emit[$]) {
            $++;
            continue;
          }
          const X = He.classNameAliases[k[$]] || k[$],
            xe = A[$];
          (X ? pe(xe, X) : ((se = xe), K(), (se = "")), $++);
        }
      }
      function $e(k, A) {
        return (
          k.scope &&
            typeof k.scope == "string" &&
            ke.openNode(He.classNameAliases[k.scope] || k.scope),
          k.beginScope &&
            (k.beginScope._wrap
              ? (pe(
                  se,
                  He.classNameAliases[k.beginScope._wrap] || k.beginScope._wrap,
                ),
                (se = ""))
              : k.beginScope._multi && (oe(k.beginScope, A), (se = ""))),
          (Y = Object.create(k, { parent: { value: Y } })),
          Y
        );
      }
      function Ye(k, A, $) {
        let W = _T(k.endRe, $);
        if (W) {
          if (k["on:end"]) {
            const X = new tp(k);
            (k["on:end"](A, X), X.isMatchIgnored && (W = !1));
          }
          if (W) {
            for (; k.endsParent && k.parent;) k = k.parent;
            return k;
          }
        }
        if (k.endsWithParent) return Ye(k.parent, A, $);
      }
      function Rt(k) {
        return Y.matcher.regexIndex === 0 ? ((se += k[0]), 1) : ((Qr = !0), 0);
      }
      function Ot(k) {
        const A = k[0],
          $ = k.rule,
          W = new tp($),
          X = [$.__beforeBegin, $["on:begin"]];
        for (const xe of X)
          if (xe && (xe(k, W), W.isMatchIgnored)) return Rt(A);
        return (
          $.skip
            ? (se += A)
            : ($.excludeBegin && (se += A),
              ne(),
              !$.returnBegin && !$.excludeBegin && (se = A)),
          $e($, k),
          $.returnBegin ? 0 : A.length
        );
      }
      function nn(k) {
        const A = k[0],
          $ = B.substring(k.index),
          W = Ye(Y, k, $);
        if (!W) return ap;
        const X = Y;
        Y.endScope && Y.endScope._wrap
          ? (ne(), pe(A, Y.endScope._wrap))
          : Y.endScope && Y.endScope._multi
            ? (ne(), oe(Y.endScope, k))
            : X.skip
              ? (se += A)
              : (X.returnEnd || X.excludeEnd || (se += A),
                ne(),
                X.excludeEnd && (se = A));
        do
          (Y.scope && ke.closeNode(),
            !Y.skip && !Y.subLanguage && (or += Y.relevance),
            (Y = Y.parent));
        while (Y !== W.parent);
        return (W.starts && $e(W.starts, k), X.returnEnd ? 0 : A.length);
      }
      function qr() {
        const k = [];
        for (let A = Y; A !== He; A = A.parent) A.scope && k.unshift(A.scope);
        k.forEach((A) => ke.openNode(A));
      }
      let rn = {};
      function ir(k, A) {
        const $ = A && A[0];
        if (((se += k), $ == null)) return (ne(), 0);
        if (
          rn.type === "begin" &&
          A.type === "end" &&
          rn.index === A.index &&
          $ === ""
        ) {
          if (((se += B.slice(A.index, A.index + 1)), !i)) {
            const W = new Error(`0 width match regex (${R})`);
            throw ((W.languageName = R), (W.badRule = rn.rule), W);
          }
          return 1;
        }
        if (((rn = A), A.type === "begin")) return Ot(A);
        if (A.type === "illegal" && !C) {
          const W = new Error(
            'Illegal lexeme "' +
              $ +
              '" for mode "' +
              (Y.scope || "<unnamed>") +
              '"',
          );
          throw ((W.mode = Y), W);
        } else if (A.type === "end") {
          const W = nn(A);
          if (W !== ap) return W;
        }
        if (A.type === "illegal" && $ === "")
          return (
            (se += `
`),
            1
          );
        if (Yr > 1e5 && Yr > A.index * 3)
          throw new Error(
            "potential infinite loop, way more iterations than matches",
          );
        return ((se += $), $.length);
      }
      const He = I(R);
      if (!He)
        throw (
          Gn(o.replace("{}", R)),
          new Error('Unknown language: "' + R + '"')
        );
      const le = rA(He);
      let vt = "",
        Y = M || le;
      const In = {},
        ke = new a.__emitter(a);
      qr();
      let se = "",
        or = 0,
        Ut = 0,
        Yr = 0,
        Qr = !1;
      try {
        if (He.__emitTokens) He.__emitTokens(B, ke);
        else {
          for (Y.matcher.considerAll(); ;) {
            (Yr++,
              Qr ? (Qr = !1) : Y.matcher.considerAll(),
              (Y.matcher.lastIndex = Ut));
            const k = Y.matcher.exec(B);
            if (!k) break;
            const A = B.substring(Ut, k.index),
              $ = ir(A, k);
            Ut = k.index + $;
          }
          ir(B.substring(Ut));
        }
        return (
          ke.finalize(),
          (vt = ke.toHTML()),
          {
            language: R,
            value: vt,
            relevance: or,
            illegal: !1,
            _emitter: ke,
            _top: Y,
          }
        );
      } catch (k) {
        if (k.message && k.message.includes("Illegal"))
          return {
            language: R,
            value: Ka(B),
            illegal: !0,
            relevance: 0,
            _illegalBy: {
              message: k.message,
              index: Ut,
              context: B.slice(Ut - 100, Ut + 100),
              mode: k.mode,
              resultSoFar: vt,
            },
            _emitter: ke,
          };
        if (i)
          return {
            language: R,
            value: Ka(B),
            illegal: !1,
            relevance: 0,
            errorRaised: k,
            _emitter: ke,
            _top: Y,
          };
        throw k;
      }
    }
    function f(R) {
      const B = {
        value: Ka(R),
        illegal: !1,
        relevance: 0,
        _top: l,
        _emitter: new a.__emitter(a),
      };
      return (B._emitter.addText(R), B);
    }
    function p(R, B) {
      B = B || a.languages || Object.keys(t);
      const C = f(R),
        M = B.filter(I)
          .filter(S)
          .map((ne) => c(ne, R, !1));
      M.unshift(C);
      const v = M.sort((ne, pe) => {
          if (ne.relevance !== pe.relevance) return pe.relevance - ne.relevance;
          if (ne.language && pe.language) {
            if (I(ne.language).supersetOf === pe.language) return 1;
            if (I(pe.language).supersetOf === ne.language) return -1;
          }
          return 0;
        }),
        [H, K] = v,
        w = H;
      return ((w.secondBest = K), w);
    }
    function g(R, B, C) {
      const M = (B && n[B]) || C;
      (R.classList.add("hljs"), R.classList.add(`language-${M}`));
    }
    function y(R) {
      let B = null;
      const C = u(R);
      if (s(C)) return;
      if (
        (V("before:highlightElement", { el: R, language: C }),
        R.dataset.highlighted)
      ) {
        console.log(
          "Element previously highlighted. To highlight again, first unset `dataset.highlighted`.",
          R,
        );
        return;
      }
      if (
        R.children.length > 0 &&
        (a.ignoreUnescapedHTML ||
          (console.warn(
            "One of your code blocks includes unescaped HTML. This is a potentially serious security risk.",
          ),
          console.warn(
            "https://github.com/highlightjs/highlight.js/wiki/security",
          ),
          console.warn("The element with unescaped HTML:"),
          console.warn(R)),
        a.throwUnescapedHTML)
      )
        throw new lA(
          "One of your code blocks includes unescaped HTML.",
          R.innerHTML,
        );
      B = R;
      const M = B.textContent,
        v = C ? d(M, { language: C, ignoreIllegals: !0 }) : p(M);
      ((R.innerHTML = v.value),
        (R.dataset.highlighted = "yes"),
        g(R, C, v.language),
        (R.result = {
          language: v.language,
          re: v.relevance,
          relevance: v.relevance,
        }),
        v.secondBest &&
          (R.secondBest = {
            language: v.secondBest.language,
            relevance: v.secondBest.relevance,
          }),
        V("after:highlightElement", { el: R, result: v, text: M }));
    }
    function E(R) {
      a = lp(a, R);
    }
    const h = () => {
      (_(),
        sr(
          "10.6.0",
          "initHighlighting() deprecated.  Use highlightAll() now.",
        ));
    };
    function m() {
      (_(),
        sr(
          "10.6.0",
          "initHighlightingOnLoad() deprecated.  Use highlightAll() now.",
        ));
    }
    let b = !1;
    function _() {
      function R() {
        _();
      }
      if (document.readyState === "loading") {
        (b || window.addEventListener("DOMContentLoaded", R, !1), (b = !0));
        return;
      }
      document.querySelectorAll(a.cssSelector).forEach(y);
    }
    function N(R, B) {
      let C = null;
      try {
        C = B(e);
      } catch (M) {
        if (
          (Gn(
            "Language definition for '{}' could not be registered.".replace(
              "{}",
              R,
            ),
          ),
          i)
        )
          Gn(M);
        else throw M;
        C = l;
      }
      (C.name || (C.name = R),
        (t[R] = C),
        (C.rawDefinition = B.bind(null, e)),
        C.aliases && U(C.aliases, { languageName: R }));
    }
    function x(R) {
      delete t[R];
      for (const B of Object.keys(n)) n[B] === R && delete n[B];
    }
    function O() {
      return Object.keys(t);
    }
    function I(R) {
      return ((R = (R || "").toLowerCase()), t[R] || t[n[R]]);
    }
    function U(R, { languageName: B }) {
      (typeof R == "string" && (R = [R]),
        R.forEach((C) => {
          n[C.toLowerCase()] = B;
        }));
    }
    function S(R) {
      const B = I(R);
      return B && !B.disableAutodetect;
    }
    function F(R) {
      (R["before:highlightBlock"] &&
        !R["before:highlightElement"] &&
        (R["before:highlightElement"] = (B) => {
          R["before:highlightBlock"](Object.assign({ block: B.el }, B));
        }),
        R["after:highlightBlock"] &&
          !R["after:highlightElement"] &&
          (R["after:highlightElement"] = (B) => {
            R["after:highlightBlock"](Object.assign({ block: B.el }, B));
          }));
    }
    function L(R) {
      (F(R), r.push(R));
    }
    function Q(R) {
      const B = r.indexOf(R);
      B !== -1 && r.splice(B, 1);
    }
    function V(R, B) {
      const C = R;
      r.forEach(function (M) {
        M[C] && M[C](B);
      });
    }
    function G(R) {
      return (
        sr("10.7.0", "highlightBlock will be removed entirely in v12.0"),
        sr("10.7.0", "Please use highlightElement now."),
        y(R)
      );
    }
    (Object.assign(e, {
      highlight: d,
      highlightAuto: p,
      highlightAll: _,
      highlightElement: y,
      highlightBlock: G,
      configure: E,
      initHighlighting: h,
      initHighlightingOnLoad: m,
      registerLanguage: N,
      unregisterLanguage: x,
      listLanguages: O,
      getLanguage: I,
      registerAliases: U,
      autoDetection: S,
      inherit: lp,
      addPlugin: L,
      removePlugin: Q,
    }),
      (e.debugMode = function () {
        i = !1;
      }),
      (e.safeMode = function () {
        i = !0;
      }),
      (e.versionString = oA),
      (e.regex = {
        concat: rr,
        lookahead: vy,
        either: Sc,
        optional: wT,
        anyNumberOfTimes: ET,
      }));
    for (const R in Do) typeof Do[R] == "object" && yy(Do[R]);
    return (Object.assign(e, Do), e);
  },
  Ur = Ty({});
Ur.newInstance = () => Ty({});
var sA = Ur;
Ur.HighlightJS = Ur;
Ur.default = Ur;
const uA = Rl(sA),
  sp = {},
  cA = "hljs-";
function dA(e) {
  const t = uA.newInstance();
  return (
    e && o(e),
    {
      highlight: n,
      highlightAuto: r,
      listLanguages: i,
      register: o,
      registerAlias: l,
      registered: a,
    }
  );
  function n(s, u, d) {
    const c = d || sp,
      f = typeof c.prefix == "string" ? c.prefix : cA;
    if (!t.getLanguage(s))
      throw new Error("Unknown language: `" + s + "` is not registered");
    t.configure({ __emitter: fA, classPrefix: f });
    const p = t.highlight(u, { ignoreIllegals: !0, language: s });
    if (p.errorRaised)
      throw new Error("Could not highlight with `Highlight.js`", {
        cause: p.errorRaised,
      });
    const g = p._emitter.root,
      y = g.data;
    return ((y.language = p.language), (y.relevance = p.relevance), g);
  }
  function r(s, u) {
    const c = (u || sp).subset || i();
    let f = -1,
      p = 0,
      g;
    for (; ++f < c.length;) {
      const y = c[f];
      if (!t.getLanguage(y)) continue;
      const E = n(y, s, u);
      E.data &&
        E.data.relevance !== void 0 &&
        E.data.relevance > p &&
        ((p = E.data.relevance), (g = E));
    }
    return (
      g || {
        type: "root",
        children: [],
        data: { language: void 0, relevance: p },
      }
    );
  }
  function i() {
    return t.listLanguages();
  }
  function o(s, u) {
    if (typeof s == "string") t.registerLanguage(s, u);
    else {
      let d;
      for (d in s) Object.hasOwn(s, d) && t.registerLanguage(d, s[d]);
    }
  }
  function l(s, u) {
    if (typeof s == "string")
      t.registerAliases(typeof u == "string" ? u : [...u], { languageName: s });
    else {
      let d;
      for (d in s)
        if (Object.hasOwn(s, d)) {
          const c = s[d];
          t.registerAliases(typeof c == "string" ? c : [...c], {
            languageName: d,
          });
        }
    }
  }
  function a(s) {
    return !!t.getLanguage(s);
  }
}
class fA {
  constructor(t) {
    ((this.options = t),
      (this.root = {
        type: "root",
        children: [],
        data: { language: void 0, relevance: 0 },
      }),
      (this.stack = [this.root]));
  }
  addText(t) {
    if (t === "") return;
    const n = this.stack[this.stack.length - 1],
      r = n.children[n.children.length - 1];
    r && r.type === "text"
      ? (r.value += t)
      : n.children.push({ type: "text", value: t });
  }
  startScope(t) {
    this.openNode(String(t));
  }
  endScope() {
    this.closeNode();
  }
  __addSublanguage(t, n) {
    const r = this.stack[this.stack.length - 1],
      i = t.root.children;
    n
      ? r.children.push({
          type: "element",
          tagName: "span",
          properties: { className: [n] },
          children: i,
        })
      : r.children.push(...i);
  }
  openNode(t) {
    const n = this,
      r = t.split(".").map(function (l, a) {
        return a ? l + "_".repeat(a) : n.options.classPrefix + l;
      }),
      i = this.stack[this.stack.length - 1],
      o = {
        type: "element",
        tagName: "span",
        properties: { className: r },
        children: [],
      };
    (i.children.push(o), this.stack.push(o));
  }
  closeNode() {
    this.stack.pop();
  }
  finalize() {}
  toHTML() {
    return "";
  }
}
const pA = {};
function hA(e) {
  const t = e || pA,
    n = t.aliases,
    r = t.detect || !1,
    i = t.languages || gT,
    o = t.plainText,
    l = t.prefix,
    a = t.subset;
  let s = "hljs";
  const u = dA(i);
  if ((n && u.registerAlias(n), l)) {
    const d = l.indexOf("-");
    s = d === -1 ? l : l.slice(0, d);
  }
  return function (d, c) {
    Jl(d, "element", function (f, p, g) {
      if (
        f.tagName !== "code" ||
        !g ||
        g.type !== "element" ||
        g.tagName !== "pre"
      )
        return;
      const y = gA(f);
      if (y === !1 || (!y && !r) || (y && o && o.includes(y))) return;
      (Array.isArray(f.properties.className) || (f.properties.className = []),
        f.properties.className.includes(s) ||
          f.properties.className.unshift(s));
      const E = HN(f, { whitespace: "pre" });
      let h;
      try {
        h = y
          ? u.highlight(y, E, { prefix: l })
          : u.highlightAuto(E, { prefix: l, subset: a });
      } catch (m) {
        const b = m;
        if (y && /Unknown language/.test(b.message)) {
          c.message("Cannot highlight as `" + y + "`, it’s not registered", {
            ancestors: [g, f],
            cause: b,
            place: f.position,
            ruleId: "missing-language",
            source: "rehype-highlight",
          });
          return;
        }
        throw b;
      }
      (!y &&
        h.data &&
        h.data.language &&
        f.properties.className.push("language-" + h.data.language),
        h.children.length > 0 && (f.children = h.children));
    });
  };
}
function gA(e) {
  const t = e.properties.className;
  let n = -1;
  if (!Array.isArray(t)) return;
  let r;
  for (; ++n < t.length;) {
    const i = String(t[n]);
    if (i === "no-highlight" || i === "nohighlight") return !1;
    (!r && i.slice(0, 5) === "lang-" && (r = i.slice(5)),
      !r && i.slice(0, 9) === "language-" && (r = i.slice(9)));
  }
  return r;
}
function mA(e) {
  const t = [],
    n = e.split(/(\$\$[\s\S]*?\$\$)/g);
  for (const r of n)
    if (r)
      if (r.startsWith("$$") && r.endsWith("$$"))
        t.push({ type: "math-display", content: r.slice(2, -2).trim() });
      else {
        const i = r.split(/(\$[^$]+\$)/g);
        for (const o of i)
          o &&
            (o.startsWith("$") && o.endsWith("$") && o.length > 2
              ? t.push({ type: "math-inline", content: o.slice(1, -1).trim() })
              : t.push({ type: "markdown", content: o }));
      }
  return t;
}
function up(e, t) {
  const n = window;
  if (!n.katex) return e;
  try {
    const r = up._c || (up._c = new Map()),
      k = t + " " + e;
    if (r.has(k)) return r.get(k);
    const o = n.katex.renderToString(e, { throwOnError: !1, displayMode: t });
    return (r.set(k, o), o);
  } catch {
    return e;
  }
}
function yA() {
  return T.jsx("div", {
    className:
      "w-9 h-9 rounded-full bg-sunset-500 flex items-center justify-center shrink-0 shadow-md shadow-orange-200",
    children: T.jsxs("svg", {
      width: "18",
      height: "18",
      viewBox: "0 0 24 24",
      fill: "none",
      stroke: "white",
      strokeWidth: "2.2",
      strokeLinecap: "round",
      strokeLinejoin: "round",
      children: [
        T.jsx("circle", { cx: "12", cy: "8", r: "4" }),
        T.jsx("path", { d: "M4 20c0-4 4-7 8-7s8 3 8 7" }),
      ],
    }),
  });
}
function bA() {
  return T.jsx("div", {
    className:
      "w-9 h-9 rounded-full bg-gradient-to-br from-lavender-500 to-sunset-400 flex items-center justify-center shrink-0 shadow-md shadow-purple-200",
    children: T.jsxs("svg", {
      width: "18",
      height: "18",
      viewBox: "0 0 24 24",
      fill: "none",
      stroke: "white",
      strokeWidth: "2.2",
      strokeLinecap: "round",
      strokeLinejoin: "round",
      children: [
        T.jsx("rect", { x: "3", y: "3", width: "18", height: "14", rx: "3" }),
        T.jsx("circle", {
          cx: "8",
          cy: "19",
          r: "1.5",
          fill: "white",
          stroke: "none",
        }),
        T.jsx("circle", {
          cx: "16",
          cy: "19",
          r: "1.5",
          fill: "white",
          stroke: "none",
        }),
        T.jsx("path", { d: "M8 19h8" }),
        T.jsx("line", { x1: "12", y1: "8", x2: "12", y2: "13" }),
        T.jsx("line", { x1: "9", y1: "11", x2: "15", y2: "11" }),
      ],
    }),
  });
}
function cp({ role: e, content: t, isStreaming: n }) {
  const r = e === "user",
    i = r ? yA : bA,
    o = D.useMemo(() => mA(t), [t]);
  return T.jsxs("div", {
    className: Or(
      "flex gap-3 py-3 px-4 max-w-3xl mx-auto w-full msg-enter",
      r && "flex-row-reverse",
    ),
    children: [
      T.jsx(i, {}),
      T.jsxs("div", {
        className: Or(
          "rounded-3xl px-5 py-3 text-sm leading-relaxed max-w-[75%] min-w-0 transition-all",
          r
            ? "bg-sunset-500 text-white rounded-br-xl shadow-md shadow-orange-200"
            : "bg-white text-foreground rounded-bl-xl border border-cream-300 shadow-sm markdown-body",
        ),
        children: [
          r
            ? T.jsx("p", { className: "whitespace-pre-wrap", children: t })
            : o.map((l, a) =>
                l.type === "math-display"
                  ? T.jsx(
                      "div",
                      {
                        dangerouslySetInnerHTML: { __html: up(l.content, !0) },
                      },
                      a,
                    )
                  : l.type === "math-inline"
                    ? T.jsx(
                        "span",
                        {
                          dangerouslySetInnerHTML: {
                            __html: up(l.content, !1),
                          },
                        },
                        a,
                      )
                    : T.jsx(
                        xS,
                        {
                          remarkPlugins: [DN],
                          rehypePlugins: [hA],
                          children: l.content,
                        },
                        a,
                      ),
              ),
          n &&
            T.jsxs("span", {
              className: "inline-flex gap-1 ml-1.5 align-text-bottom",
              children: [
                T.jsx("span", {
                  className:
                    "w-1.5 h-4 bg-sunset-400 rounded-full animate-bounce",
                  style: { animationDelay: "0ms" },
                }),
                T.jsx("span", {
                  className:
                    "w-1.5 h-4 bg-lavender-400 rounded-full animate-bounce",
                  style: { animationDelay: "150ms" },
                }),
                T.jsx("span", {
                  className:
                    "w-1.5 h-4 bg-sunset-300 rounded-full animate-bounce",
                  style: { animationDelay: "300ms" },
                }),
              ],
            }),
        ],
      }),
    ],
  });
}
function vA() {
  return T.jsx("div", {
    className: "flex-1 flex items-center justify-center welcome-grid",
    children: T.jsxs("div", {
      className: "text-center max-w-md",
      children: [
        T.jsxs("div", {
          className: "mb-8 relative mx-auto w-28 h-28",
          children: [
            T.jsx("div", {
              className:
                "absolute inset-0 bg-gradient-to-br from-sunset-400 to-lavender-500 rounded-3xl rotate-6 opacity-20 blur-xl",
            }),
            T.jsx("div", {
              className:
                "relative welcome-icon bg-white rounded-3xl p-5 shadow-xl shadow-orange-100 border border-cream-200",
              children: T.jsxs("svg", {
                viewBox: "0 0 60 60",
                fill: "none",
                className: "w-full h-full",
                children: [
                  T.jsx("circle", {
                    cx: "30",
                    cy: "30",
                    r: "24",
                    fill: "url(#grad)",
                    opacity: "0.12",
                  }),
                  T.jsx("rect", {
                    x: "18",
                    y: "20",
                    width: "24",
                    height: "16",
                    rx: "3",
                    stroke: "#FF7B42",
                    strokeWidth: "2.5",
                  }),
                  T.jsx("line", {
                    x1: "24",
                    y1: "28",
                    x2: "36",
                    y2: "28",
                    stroke: "#8B7FFF",
                    strokeWidth: "2",
                    strokeLinecap: "round",
                  }),
                  T.jsx("line", {
                    x1: "24",
                    y1: "32",
                    x2: "32",
                    y2: "32",
                    stroke: "#FFB088",
                    strokeWidth: "2",
                    strokeLinecap: "round",
                  }),
                  T.jsx("circle", {
                    cx: "40",
                    cy: "22",
                    r: "6",
                    fill: "#8B7FFF",
                    opacity: "0.15",
                  }),
                  T.jsx("path", {
                    d: "M42 20 L48 22 L44 26 L38 24 Z",
                    fill: "#FF7B42",
                    opacity: "0.3",
                  }),
                  T.jsx("defs", {
                    children: T.jsxs("radialGradient", {
                      id: "grad",
                      cx: "0",
                      cy: "0",
                      r: "1",
                      children: [
                        T.jsx("stop", { stopColor: "#FF7B42" }),
                        T.jsx("stop", { offset: "1", stopColor: "#8B7FFF" }),
                      ],
                    }),
                  }),
                ],
              }),
            }),
          ],
        }),
        T.jsxs("h1", {
          className: "text-2xl font-bold mb-2 font-brand text-foreground",
          children: [
            "你好，我是 WirelessAgent ",
            T.jsx("span", { className: "text-2xl", children: "👋" }),
          ],
        }),
        T.jsx("p", {
          className: "text-muted-foreground text-sm leading-relaxed mb-8",
          children:
            "无线通信 AI 辅导助手，随时为你解答习题、讲解知识点、检索标准文档",
        }),
        T.jsx("div", {
          className: "grid grid-cols-3 gap-3",
          children: [
            {
              icon: nw,
              label: "习题解答",
              color: "text-sunset-500",
              bg: "bg-accent",
            },
            {
              icon: xl,
              label: "知识讲解",
              color: "text-lavender-500",
              bg: "bg-lavender-100",
            },
            {
              icon: iw,
              label: "标准检索",
              color: "text-amber-600",
              bg: "bg-amber-50",
            },
          ].map(({ icon: e, label: t, color: n, bg: r }) =>
            T.jsxs(
              "div",
              {
                className: `${r} rounded-2xl p-4 transition-transform hover:scale-105 duration-200 cursor-default`,
                children: [
                  T.jsx(e, { className: `w-6 h-6 ${n} mx-auto mb-2` }),
                  T.jsx("p", {
                    className: "text-xs font-medium text-muted-foreground",
                    children: t,
                  }),
                ],
              },
              t,
            ),
          ),
        }),
        T.jsxs("div", {
          className:
            "mt-8 inline-flex items-center gap-2 text-xs text-muted-foreground/50 bg-white/60 px-4 py-2 rounded-full border border-cream-200",
          children: [
            T.jsx(nc, { className: "w-3.5 h-3.5 text-sunset-400" }),
            "直接在下方输入问题开始吧",
          ],
        }),
      ],
    }),
  });
}
function EA({ messages: e, streamingContent: t }) {
  const n = D.useRef(null),
    r = D.useRef(null),
    i = D.useRef(!0),
    o = D.useRef(0);
  (D.useEffect(() => {
    (e.length > o.current && (i.current = !0), (o.current = e.length));
  }, [e.length]),
    D.useEffect(() => {
      if (!i.current) return;
      const a = r.current;
      a &&
        requestAnimationFrame(() => {
          a.scrollTop = a.scrollHeight;
        });
    }, [e, t]));
  const l = () => {
    const a = r.current;
    a && (i.current = a.scrollTop + a.clientHeight >= a.scrollHeight - 80);
  };
  return e.length === 0 && !t
    ? T.jsx(vA, {})
    : T.jsxs("div", {
        ref: r,
        onScroll: l,
        className: "flex-1 overflow-y-auto py-4",
        children: [
          e.map((a) => T.jsx(cp, { role: a.role, content: a.content }, a.id)),
          t && T.jsx(cp, { role: "assistant", content: t, isStreaming: !0 }),
          T.jsx("div", { ref: n }),
        ],
      });
}
let wkPrefill = "";
function wA({ onSend: e, disabled: t, loading: n }) {
  const [r, i] = D.useState(() => {
    const v = wkPrefill;
    wkPrefill = "";
    return v;
  }),
    [o, l] = D.useState([]),
    a = D.useRef(null),
    s = () => {
      var f;
      const c = r.trim();
      (!c && o.length === 0) ||
        (e(c || "(uploaded files)", o.length > 0 ? o : void 0),
        i(""),
        l([]),
        (f = a.current) == null || f.focus());
    },
    u = (c) => {
      c.key === "Enter" && !c.shiftKey && (c.preventDefault(), s());
    },
    d = (c) => {
      c && l((f) => [...f, ...Array.from(c)]);
    };
  return T.jsxs("div", {
    className:
      "border-t border-cream-300 bg-gradient-to-t from-cream-50 to-transparent px-4 pb-6 pt-3",
    children: [
      o.length > 0 &&
        T.jsx("div", {
          className: "flex gap-2 mb-3 flex-wrap max-w-3xl mx-auto",
          children: o.map((c, f) =>
            T.jsxs(
              "span",
              {
                className:
                  "flex items-center gap-1.5 bg-accent text-accent-foreground text-xs px-3 py-1.5 rounded-xl font-medium",
                children: [
                  T.jsx(Kd, { className: "w-3 h-3 opacity-60" }),
                  c.name,
                  T.jsx("button", {
                    onClick: () => l(o.filter((p, g) => g !== f)),
                    className:
                      "hover:bg-orange-200 rounded-full p-0.5 transition-colors",
                    children: T.jsx(sw, { className: "w-3 h-3" }),
                  }),
                ],
              },
              f,
            ),
          ),
        }),
      T.jsxs("div", {
        className: "flex items-end gap-2.5 max-w-3xl mx-auto",
        children: [
          T.jsxs("label", {
            className: Or(
              "p-2.5 rounded-2xl cursor-pointer text-muted-foreground hover:text-sunset-500 hover:bg-accent transition-all duration-200",
              t && "opacity-50 pointer-events-none",
            ),
            children: [
              T.jsx(Kd, { className: "w-4.5 h-4.5" }),
              T.jsx("input", {
                type: "file",
                className: "hidden",
                multiple: !0,
                onChange: (c) => d(c.target.files),
              }),
            ],
          }),
          T.jsx("div", {
            className:
              "flex-1 rounded-2xl bg-white border border-cream-300 shadow-sm chat-input-glow transition-shadow duration-300",
            children: T.jsx("textarea", {
              ref: a,
              value: r,
              onChange: (c) => i(c.target.value),
              onKeyDown: u,
              placeholder: t
                ? "Creating session..."
                : "Ask me anything about wireless communications...",
              disabled: t,
              rows: 1,
              className: `w-full bg-transparent px-4 py-3 text-sm placeholder:text-muted-foreground/60
                       focus:outline-none resize-none max-h-32 disabled:opacity-50 font-sans`,
            }),
          }),
          T.jsx("button", {
            onClick: s,
            disabled: t || (!r.trim() && o.length === 0),
            className: `group p-2.5 rounded-2xl bg-sunset-500 hover:bg-sunset-600 disabled:opacity-40
                     disabled:cursor-not-allowed transition-all duration-200 text-white shadow-md shadow-orange-200
                     hover:shadow-lg hover:shadow-orange-200 active:scale-95`,
            children: n
              ? T.jsx(nc, { className: "w-4.5 h-4.5 animate-spin" })
              : T.jsx(lw, {
                  className:
                    "w-4.5 h-4.5 group-hover:translate-x-0.5 transition-transform",
                }),
          }),
        ],
      }),
      T.jsx("p", {
        className:
          "text-center text-xs text-muted-foreground/50 mt-2.5 font-medium",
        children: "WirelessAgent may make mistakes. Verify important info.",
      }),
    ],
  });
}
function xA() {
  const [e, t] = D.useState([]),
    [n, r] = D.useState(!0),
    i = D.useCallback(async () => {
      try {
        const a = await Yt.listSessions();
        a.ok && t(await a.json());
      } catch {
      } finally {
        r(!1);
      }
    }, []);
  D.useEffect(() => {
    i();
  }, [i]);
  const o = D.useCallback(async () => {
      const a = await Yt.createSession();
      if (a.ok) {
        const s = await a.json();
        return (t((u) => [s, ...u]), s);
      }
    }, []),
    l = D.useCallback(async (a) => {
      (await Yt.deleteSession(a)).ok && t((u) => u.filter((d) => d.id !== a));
    }, []);
  return { sessions: e, loading: n, refresh: i, create: o, remove: l };
}
function _A() {
  const [e, t] = D.useState([]),
    [n, r] = D.useState(""),
    [i, o] = D.useState(!1),
    l = D.useRef(null),
    a = D.useCallback(async (d, c) => {
      var g;
      const f = { id: crypto.randomUUID(), role: "user", content: c };
      (t((y) => [...y, f]), o(!0), r(""));
      const p = new AbortController();
      l.current = p;
      try {
        const E =
          (g = (await Yt.chatStream(d, c)).body) == null
            ? void 0
            : g.getReader();
        if (!E) throw new Error("No response body");
        const h = new TextDecoder();
        let m = "",
          z = !1;
        for (;;) {
          const { done: b, value: _ } = await E.read();
          if (b) break;
          const x = h.decode(_, { stream: !0 }).split(`
`);
          for (const O of x)
            if (O.startsWith("data: ")) {
              const I = O.slice(6);
              try {
                const U = JSON.parse(I);
                if (
                  (U.token &&
                    ((m += U.token),
                    z ||
                      ((z = !0),
                      requestAnimationFrame(() => {
                        (r(m), (z = !1));
                      }))),
                  U.error)
                ) {
                  const F =
                    (m
                      ? m +
                        `

---
`
                      : "") +
                    "⚠️ " +
                    U.error;
                  (r(F), (m = F));
                }
                if (U.done) {
                  const S = {
                    id: crypto.randomUUID(),
                    role: "assistant",
                    content: m,
                  };
                  (t((F) => [...F, S]), r(""));
                }
              } catch {}
            }
        }
      } catch (y) {
        y.name !== "AbortError" &&
          t((E) => [
            ...E,
            {
              id: crypto.randomUUID(),
              role: "assistant",
              content: "⚠️ AI 服务暂时不可用，请稍后重试",
            },
          ]);
      } finally {
        o(!1);
      }
    }, []),
    s = D.useCallback(() => {
      var d;
      ((d = l.current) == null || d.abort(), o(!1));
    }, []),
    u = D.useCallback(() => {
      (t([]), r(""));
    }, []);
  return {
    messages: e,
    streaming: n,
    loading: i,
    send: a,
    stop: s,
    clear: u,
    setMessages: t,
  };
}
function kA() {
  const e = tc(),
    { sessions: t, loading: n, create: r, remove: i } = xA(),
    {
      messages: o,
      streaming: l,
      loading: a,
      send: s,
      clear: u,
      setMessages: d,
    } = _A(),
    [c, f] = D.useState(null);
  (D.useEffect(() => {
    localStorage.getItem("token") ||
      Yt.guest()
        .then(async (m) => {
          if (m.ok) {
            const b = await m.json();
            (localStorage.setItem("token", b.access_token),
              window.location.reload());
          }
        })
        .catch(() => e("/login"));
  }, [e]),
    D.useEffect(() => {
      !n && t.length > 0 && !c && f(t[0].id);
    }, [t, n, c]),
    D.useEffect(() => {
      !n &&
        t.length === 0 &&
        !c &&
        r()
          .then((h) => {
            h && f(h.id);
          })
          .catch(() => {});
    }, [n, t.length, c, r]));
  const p = async (h) => {
      (f(h), u());
      try {
        const m = await Yt.getMessages(h);
        if (m.ok) {
          const b = await m.json();
          d(b.map((_) => ({ id: _.id, role: _.role, content: _.content })));
        }
      } catch {}
    },
    g = D.useCallback(async () => {
      const h = await r();
      h && (f(h.id), u());
    }, [r, u]),
    y = D.useCallback(
      (h) => {
        (i(h), c === h && (f(null), u()));
      },
      [i, c, u],
    ),
    E = async (h) => {
      if (c) s(c, h);
      else {
        const m = await r();
        if (!m) return;
        (f(m.id), s(m.id, h));
      }
    };
  return T.jsxs("div", {
    className: "flex h-screen overflow-hidden bg-cream-100",
    children: [
      T.jsx(Ww, {
        mode: "chat",
        sessions: t,
        activeId: c,
        onSelect: p,
        onCreate: g,
        onDelete: y,
      }),
      T.jsxs("main", {
        className: "flex-1 flex flex-col min-w-0 bg-cream-50",
        children: [
          T.jsx(EA, { messages: o, streamingContent: l }),
          T.jsx("div", {
            className: "shrink-0",
            children: T.jsx(wA, { onSend: E, loading: a }),
          }),
        ],
      }),
    ],
  });
}
function WkRagSearch() {
  const [q, setQ] = D.useState("");
  const [res, setRes] = D.useState(null);
  const [loading, setLoading] = D.useState(!1);
  const [err, setErr] = D.useState("");
  const run = async () => {
    const query = q.trim();
    if (!query) return;
    setLoading(!0);
    setErr("");
    setRes(null);
    try {
      const r = await Yt.search(query);
      if (r.ok) setRes(await r.json());
      else setErr("检索失败，请稍后重试");
    } catch {
      setErr("网络错误，请检查连接后重试");
    } finally {
      setLoading(!1);
    }
  };
  const items =
    res == null
      ? []
      : Array.isArray(res)
        ? res
        : res.results || res.data || res.chunks || [];
  return T.jsxs("div", {
    className: "flex-1 flex flex-col min-w-0",
    children: [
      T.jsxs("div", {
        className: "p-6 pb-4 border-b border-cream-200",
        children: [
          T.jsx("h2", {
            className: "font-brand text-2xl text-foreground",
            children: "标准检索",
          }),
          T.jsx("p", {
            className: "text-sm text-muted-foreground mt-1",
            children: "在知识库中语义检索 3GPP / ITU / IEEE 标准与课程知识点",
          }),
        ],
      }),
      T.jsx("div", {
        className: "px-6 py-4",
        children: T.jsxs("div", {
          className: "flex gap-2 max-w-2xl",
          children: [
            T.jsx("input", {
              value: q,
              onChange: (e) => setQ(e.target.value),
              onKeyDown: (e) => e.key === "Enter" && run(),
              placeholder: "输入关键词或问题，如：5G NR 子载波间隔",
              className:
                "flex-1 rounded-2xl border border-cream-300 bg-white px-4 py-3 text-sm placeholder:text-muted-foreground/50 focus:outline-none focus:border-sunset-400",
            }),
            T.jsxs("button", {
              onClick: run,
              disabled: loading,
              className:
                "px-5 py-3 rounded-2xl bg-sunset-500 hover:bg-sunset-600 disabled:opacity-40 text-white text-sm font-medium transition-all duration-200",
              children: [
                loading
                  ? T.jsx(nc, { className: "w-4 h-4 animate-spin" })
                  : T.jsx(WkSearch, { className: "w-4 h-4" }),
              ],
            }),
          ],
        }),
      }),
      T.jsx("div", {
        className: "flex-1 overflow-y-auto px-6 pb-6",
        children: err
          ? T.jsx("p", { className: "text-sm text-red-400", children: err })
          : res == null
            ? T.jsx("p", {
                className: "text-sm text-muted-foreground/50 mt-8 text-center",
                children: "输入查询后回车或点击搜索按钮",
              })
            : items.length === 0
              ? T.jsx("p", {
                  className: "text-sm text-muted-foreground/50 mt-8 text-center",
                  children: "未找到相关内容",
                })
              : T.jsxs("div", {
                  className: "space-y-3",
                  children: items.map((it, idx) => {
                    const title =
                      it.title || it.doc_id || it.id || it.source ||
                      "结果 " + (idx + 1);
                    const bodyText =
                      it.content || it.text || it.chunk || it.snippet || "";
                    return T.jsxs(
                      "div",
                      {
                        key: idx,
                        className:
                          "bg-white rounded-2xl border border-cream-200 p-4 shadow-sm",
                        children: [
                          T.jsxs("div", {
                            className: "flex items-center justify-between gap-3",
                            children: [
                              T.jsx("p", {
                                className: "text-sm font-medium text-foreground",
                                children: title,
                              }),
                              it.score != null &&
                                T.jsx("span", {
                                  className: "text-xs text-sunset-500 shrink-0",
                                  children:
                                    "相关度 " +
                                    Math.round(
                                      (it.score <= 1
                                        ? it.score
                                        : Math.min(1, it.score / 100)) * 100,
                                    ) +
                                    "%",
                                }),
                            ],
                          }),
                          bodyText &&
                            T.jsx("p", {
                              className:
                                "text-sm text-muted-foreground mt-2 leading-relaxed",
                              children: bodyText,
                            }),
                        ],
                      },
                      idx,
                    );
                  }),
                }),
      }),
    ],
  });
}
function WkFileUpload() {
  const [files, setFiles] = D.useState([]);
  const [uploading, setUploading] = D.useState(!1);
  const [results, setResults] = D.useState([]);
  const [err, setErr] = D.useState("");
  const pick = (e) => e.target.files && setFiles(Array.from(e.target.files));
  const run = async () => {
    if (files.length === 0) return;
    setUploading(!0);
    setErr("");
    setResults([]);
    try {
      const out = [];
      for (const f of files) {
        const r = await Yt.upload(f);
        if (r.ok) {
          const d = await r.json().catch(() => ({}));
          out.push({ name: f.name, ok: !0, msg: d.message || d.filename || "上传成功" });
        } else {
          out.push({ name: f.name, ok: !1, msg: "上传失败（" + r.status + "）" });
        }
      }
      setResults(out);
      setFiles([]);
    } catch {
      setErr("网络错误，请检查连接后重试");
    } finally {
      setUploading(!1);
    }
  };
  return T.jsxs("div", {
    className: "flex-1 flex flex-col min-w-0",
    children: [
      T.jsxs("div", {
        className: "p-6 pb-4 border-b border-cream-200",
        children: [
          T.jsx("h2", {
            className: "font-brand text-2xl text-foreground",
            children: "文件上传",
          }),
          T.jsx("p", {
            className: "text-sm text-muted-foreground mt-1",
            children: "上传课件 / 标准文档，供 AI 在对话中参考",
          }),
        ],
      }),
      T.jsx("div", {
        className: "flex-1 overflow-y-auto px-6 py-6",
        children: [
          T.jsxs("label", {
            className:
              "flex flex-col items-center justify-center gap-3 border-2 border-dashed border-cream-300 rounded-3xl p-10 cursor-pointer hover:border-sunset-400 transition-colors",
            children: [
              T.jsx(WkUpload, { className: "w-10 h-10 text-sunset-400" }),
              T.jsx("p", {
                className: "text-sm text-muted-foreground",
                children: "点击选择文件（支持多选）",
              }),
              T.jsx("input", {
                type: "file",
                multiple: !0,
                className: "hidden",
                onChange: pick,
              }),
            ],
          }),
          files.length > 0 &&
            T.jsxs("div", {
              className: "mt-4 space-y-2",
              children: [
                files.map((f, idx) =>
                  T.jsx("p", {
                    key: idx,
                    className: "text-sm text-muted-foreground",
                    children: f.name,
                  }),
                ),
                T.jsxs("button", {
                  onClick: run,
                  disabled: uploading,
                  className:
                    "px-5 py-2.5 rounded-2xl bg-sunset-500 hover:bg-sunset-600 disabled:opacity-40 text-white text-sm font-medium transition-all duration-200",
                  children: [uploading ? "上传中…" : "开始上传"],
                }),
              ],
            }),
          err &&
            T.jsx("p", { className: "text-sm text-red-400 mt-4", children: err }),
          results.length > 0 &&
            T.jsxs("div", {
              className: "mt-6 space-y-2",
              children: results.map((r, idx) =>
                T.jsx("p", {
                  key: idx,
                  className: Or("text-sm", r.ok ? "text-sunset-500" : "text-red-400"),
                  children: r.name + " — " + r.msg,
                }),
              ),
            }),
        ],
      }),
    ],
  });
}
function WkHomework() {
  const e = tc();
  const [text, setText] = D.useState("");
  const go = () => {
    wkPrefill = "请帮我解答这道题：\n" + (text.trim() ? text.trim() : "");
    e("/");
  };
  return T.jsxs("div", {
    className: "flex-1 flex flex-col min-w-0",
    children: [
      T.jsxs("div", {
        className: "p-6 pb-4 border-b border-cream-200",
        children: [
          T.jsx("h2", {
            className: "font-brand text-2xl text-foreground",
            children: "习题解答",
          }),
          T.jsx("p", {
            className: "text-sm text-muted-foreground mt-1",
            children: "粘贴题目，跳转到对话并自动带入，由 AI 分步解答",
          }),
        ],
      }),
      T.jsxs("div", {
        className: "flex-1 overflow-y-auto px-6 py-6",
        children: [
          T.jsx("textarea", {
            value: text,
            onChange: (e) => setText(e.target.value),
            placeholder:
              "在此粘贴要解答的习题，例如：\n某信道带宽 10MHz，SNR=20dB，求信道容量……",
            rows: 8,
            className:
              "w-full max-w-2xl rounded-2xl border border-cream-300 bg-white px-4 py-3 text-sm placeholder:text-muted-foreground/50 focus:outline-none focus:border-sunset-400 resize-none",
          }),
          T.jsx("div", {
            className: "mt-4",
            children: T.jsxs("button", {
              onClick: go,
              className:
                "px-5 py-2.5 rounded-2xl bg-sunset-500 hover:bg-sunset-600 text-white text-sm font-medium transition-all duration-200",
              children: [
                T.jsx(nw, { className: "w-4 h-4 inline mr-1.5" }),
                "去对话解答",
              ],
            }),
          }),
        ],
      }),
    ],
  });
}
function WkDigestPage() {
  const [s, t] = D.useState(null),
    [r, n] = D.useState(!1),
    [m, u] = D.useState(""),
    [k, c] = D.useState(0),
    load = () =>
      fetch("/api/digest/status")
        .then((x) => x.json())
        .then(t)
        .catch(() => t({})),
    run = async () => {
      (n(!0), u("正在生成最新论文速递…"));
      try {
        const x = await fetch("/api/digest/run?days=1&max_papers=20", {
          method: "POST",
        });
        const j = await x.json();
        u(j.success ? "生成完成" : "失败：" + (j.error || j.detail || "未知错误"));
        (c((v) => v + 1), load());
      } catch (e) {
        u("网络错误：" + (e && e.message ? e.message : e));
      } finally {
        n(!1);
      }
    };
  D.useEffect(() => {
    load();
  }, []);
  return T.jsxs("div", {
    className: "flex h-screen overflow-hidden bg-cream-100",
    children: [
      T.jsx(Ww, { mode: "digest" }),
      T.jsxs("main", {
        className: "flex-1 flex flex-col min-w-0 bg-cream-50",
        children: [
          T.jsxs("div", {
            className:
              "flex items-center justify-between gap-4 px-6 py-4 border-b border-cream-200 bg-white",
            children: [
              T.jsxs("div", {
                children: [
                  T.jsx("h1", {
                    className: "text-lg font-bold text-foreground",
                    children: "论文速递",
                  }),
                  T.jsx("p", {
                    className: "text-sm text-muted-foreground",
                    children: "每日 24 点自动汇总 arXiv 无线通信领域最新论文",
                  }),
                ],
              }),
              T.jsxs("div", {
                className: "flex items-center gap-3",
                children: [
                  m
                    ? T.jsx("span", {
                        className: "text-sm text-muted-foreground",
                        children: m,
                      })
                    : null,
                  r
                    ? T.jsx("span", {
                        className: "text-sm text-sunset-500",
                        children: "生成中，请稍候…",
                      })
                    : T.jsx("button", {
                        onClick: run,
                        className:
                          "px-4 py-2 rounded-lg text-sm font-medium bg-sunset-500 text-white hover:bg-sunset-600 transition-colors",
                        children: "立即生成",
                      }),
                ],
              }),
            ],
          }),
          T.jsx("iframe", {
            key: k,
            src: "/api/digest/latest",
            className: "flex-1 w-full border-0 bg-white",
            title: "论文速递报告",
          }),
        ],
      }),
    ],
  });
}

function WkWorkPage() {
  const [v, setV] = D.useState("rag");
  return T.jsxs("div", {
    className: "flex h-screen overflow-hidden bg-cream-100",
    children: [
      T.jsx(Ww, { mode: "work", workView: v, onWorkView: setV }),
      T.jsxs("main", {
        className: "flex-1 flex flex-col min-w-0 bg-cream-50",
        children: [
          v === "rag"
            ? T.jsx(WkRagSearch, {})
            : v === "upload"
              ? T.jsx(WkFileUpload, {})
              : T.jsx(WkHomework, {}),
        ],
      }),
    ],
  });
}

const PpApi = {
  list: (q, cat, limit, offset) => {
    const p = new URLSearchParams();
    if (q) p.set("q", q);
    if (cat) p.set("category", cat);
    p.set("limit", String(limit || 50));
    p.set("offset", String(offset || 0));
    return ln(`/papers/?${p.toString()}`);
  },
  get: (id) => ln(`/papers/${id}`),
  refresh: (days, max) => ln(`/papers/refresh?days=${days}&max_papers=${max}`, { method: "POST" }),
  messages: (id) => ln(`/papers/${id}/messages`),
  ask: (id, question) =>
    fetch(`${Hs}/papers/${id}/ask`, {
      method: "POST",
      headers: { "Content-Type": "application/json", Authorization: `Bearer ${js()}` },
      body: JSON.stringify({ question }),
    }),
};
function PpList() {
  const e = tc();
  const [papers, setPapers] = D.useState(null);
  const [q, setQ] = D.useState("");
  const [loading, setLoading] = D.useState(!0);
  const [refreshing, setRefreshing] = D.useState(!1);
  const [msg, setMsg] = D.useState("");
  const [err, setErr] = D.useState("");
  const load = D.useCallback(async (query) => {
    setLoading(!0);
    setErr("");
    try {
      const r = await PpApi.list(query, null, 50, 0);
      if (r.ok) setPapers(await r.json());
      else setErr("加载失败，请稍后重试");
    } catch {
      setErr("网络错误，请检查连接后重试");
    } finally {
      setLoading(!1);
    }
  }, []);
  D.useEffect(() => {
    load("");
  }, [load]);
  const doRefresh = async () => {
    setRefreshing(!0);
    setMsg("");
    setErr("");
    try {
      const r = await PpApi.refresh(7, 20);
      const d = await r.json().catch(() => ({}));
      if (r.ok) {
        setMsg("已刷新：新增 " + (d.new ?? 0) + " 篇，更新 " + (d.updated ?? 0) + " 篇");
        await load("");
      } else {
        setErr("刷新失败：" + (d.detail || r.status || "未知错误"));
      }
    } catch {
      setErr("刷新失败：网络错误");
    } finally {
      setRefreshing(!1);
    }
  };
  const items = Array.isArray(papers) ? papers : [];
  return T.jsxs("div", {
    className: "flex h-screen overflow-hidden bg-cream-100",
    children: [
      T.jsx(Ww, { mode: "papers" }),
      T.jsxs("main", {
        className: "flex-1 flex flex-col min-w-0 bg-cream-50",
        children: [
          T.jsxs("div", {
            className: "p-6 pb-4 border-b border-cream-200",
            children: [
              T.jsx("h2", { className: "font-brand text-2xl text-foreground", children: "论文答疑 · Agent2Paper" }),
              T.jsx("p", { className: "text-sm text-muted-foreground mt-1", children: "浏览最新无线通信论文，点击任意一篇与虚拟作者一对一对话" }),
            ],
          }),
          T.jsxs("div", {
            className: "px-6 py-4 flex flex-wrap gap-2 items-center",
            children: [
              T.jsx("input", {
                value: q,
                onChange: (ev) => setQ(ev.target.value),
                onKeyDown: (ev) => ev.key === "Enter" && load(q.trim()),
                placeholder: "搜索标题 / 摘要…",
                className: "flex-1 rounded-2xl border border-cream-300 bg-white px-4 py-2.5 text-sm placeholder:text-muted-foreground/50 focus:outline-none focus:border-sunset-400",
              }),
              T.jsx("button", {
                onClick: () => load(q.trim()),
                className: "px-4 py-2.5 rounded-2xl bg-cream-100 border border-cream-200 text-sm font-medium hover:bg-white/60 transition-all duration-200",
                children: "搜索",
              }),
              T.jsxs("button", {
                onClick: doRefresh,
                disabled: refreshing,
                className: "px-4 py-2.5 rounded-2xl bg-sunset-500 hover:bg-sunset-600 disabled:opacity-40 text-white text-sm font-medium transition-all duration-200",
                children: refreshing ? "刷新中…" : "刷新论文",
              }),
            ],
          }),
          msg && T.jsx("p", { className: "px-6 text-sm text-sunset-500", children: msg }),
          err && T.jsx("p", { className: "px-6 text-sm text-red-400", children: err }),
          T.jsx("div", {
            className: "flex-1 overflow-y-auto px-6 pb-6",
            children: loading
              ? T.jsx("p", { className: "text-sm text-muted-foreground/50 mt-8 text-center", children: "加载中…" })
              : items.length === 0
                ? T.jsx("p", { className: "text-sm text-muted-foreground/50 mt-8 text-center", children: "暂无论文，点击「刷新论文」拉取最新 arXiv 论文" })
                : T.jsxs("div", {
                    className: "space-y-3",
                    children: items.map((p) => {
                      const authors = Array.isArray(p.authors) ? p.authors.slice(0, 3).join(", ") + (p.authors.length > 3 ? " 等" : "") : "";
                      return T.jsxs(
                        "div",
                        {
                          key: p.arxiv_id,
                          onClick: () => e(`/papers/${p.arxiv_id}`),
                          className: "bg-white rounded-2xl border border-cream-200 p-4 shadow-sm cursor-pointer transition-colors",
                          children: [
                            T.jsxs("div", {
                              className: "flex items-start justify-between gap-3",
                              children: [
                                T.jsx("p", { className: "text-sm font-medium text-foreground leading-relaxed", children: p.title_zh || p.title }),
                                T.jsx("span", { className: "text-xs text-muted-foreground/60 shrink-0 mt-1", children: p.arxiv_id }),
                              ],
                            }),
                            p.title_zh && p.title && T.jsx("p", { className: "text-xs text-muted-foreground/70 mt-1 truncate", children: p.title }),
                            authors && T.jsx("p", { className: "text-xs text-muted-foreground mt-2", children: authors }),
                            (p.abstract_zh || p.abstract) && T.jsx("p", { className: "text-sm text-muted-foreground mt-2 leading-relaxed", children: p.abstract_zh || p.abstract }),
                            T.jsx("p", { className: "text-xs text-sunset-500 mt-2 font-medium", children: "与虚拟作者对话 →" }),
                          ],
                        },
                        p.arxiv_id,
                      );
                    }),
                  }),
          }),
        ],
      }),
    ],
  });
}
function PpChat() {
  const loc = ec();
  const e = tc();
  const id = ((loc.pathname.match(/\/papers\/([^/]+)/) || [])[1] || "").replace(/\/+$/, "");
  const [paper, setPaper] = D.useState(null);
  const [messages, setMessages] = D.useState([]);
  const [streaming, setStreaming] = D.useState("");
  const [loading, setLoading] = D.useState(!1);
  D.useEffect(() => {
    if (!id) return;
    let alive = !0;
    (async () => {
      try {
        const r = await PpApi.get(id);
        if (r.ok && alive) setPaper(await r.json());
      } catch {}
      try {
        const r = await PpApi.messages(id);
        if (r.ok && alive)
          setMessages((await r.json()).map((m) => ({ id: crypto.randomUUID(), role: m.role, content: m.content })));
      } catch {}
    })();
    return () => {
      alive = !1;
    };
  }, [id]);
  const send = async (text) => {
    const msg = (text || "").trim();
    if (!msg || !id) return;
    setMessages((m) => [...m, { id: crypto.randomUUID(), role: "user", content: msg }]);
    setLoading(!0);
    let full = "";
    try {
      const resp = await PpApi.ask(id, msg);
      if (!resp.body) throw new Error("No body");
      const reader = resp.body.getReader();
      const dec = new TextDecoder();
      for (;;) {
        const { done, value } = await reader.read();
        if (done) break;
        for (const line of dec.decode(value, { stream: !0 }).split("\n")) {
          if (line.startsWith("data: ")) {
            try {
              const u = JSON.parse(line.slice(6));
              if (u.token) {
                full += u.token;
                setStreaming(full);
              }
              if (u.error) {
                setStreaming((full ? full + "\n\n---\n" : "") + "⚠️ " + u.error);
                full = "";
              }
              if (u.done) {
                setMessages((m) => [...m, { id: crypto.randomUUID(), role: "assistant", content: full }]);
                setStreaming("");
              }
            } catch {}
          }
        }
      }
    } catch {
      setMessages((m) => [...m, { id: crypto.randomUUID(), role: "assistant", content: "⚠️ AI 服务暂时不可用，请稍后重试" }]);
      setStreaming("");
    } finally {
      setLoading(!1);
    }
  };
  return T.jsxs("div", {
    className: "flex h-screen overflow-hidden bg-cream-100",
    children: [
      T.jsx(Ww, { mode: "papers" }),
      T.jsxs("main", {
        className: "flex-1 flex flex-col min-w-0 bg-cream-50",
        children: [
          T.jsxs("div", {
            className: "px-6 py-3 border-b border-cream-200 bg-white flex items-center gap-3",
            children: [
              T.jsx("button", {
                onClick: () => e("/papers"),
                className: "text-xs text-muted-foreground hover:text-sunset-500 transition-colors shrink-0",
                children: "← 返回列表",
              }),
              T.jsx("h2", {
                className: "font-brand text-base text-foreground leading-relaxed truncate",
                children: (paper && (paper.title_zh || paper.title)) || "加载论文…",
              }),
            ],
          }),
          T.jsxs("div", {
            className: "flex-1 flex min-h-0",
            children: [
              T.jsx("div", {
                style: { width: "45%", minWidth: 320, maxWidth: 560 },
                className: "h-full overflow-y-auto border-r border-cream-200 bg-white",
                children: T.jsxs("div", {
                  className: "p-6",
                  children: [
                    paper
                      ? T.jsx("h3", {
                          className: "font-brand text-xl text-foreground leading-relaxed",
                          children: paper.title_zh || paper.title,
                        })
                      : T.jsx("p", { className: "text-sm text-muted-foreground/50", children: "加载论文…" }),
                    paper && paper.title_zh && paper.title && T.jsx("p", {
                      className: "text-sm text-muted-foreground mt-2 leading-relaxed",
                      children: paper.title,
                    }),
                    paper && T.jsx("p", {
                      className: "text-xs text-muted-foreground mt-4",
                      children: "作者：" + (Array.isArray(paper.authors) ? paper.authors.join(", ") : ""),
                    }),
                    paper && (paper.primary_category || paper.published) && T.jsx("p", {
                      className: "text-xs text-muted-foreground mt-1",
                      children: [paper.primary_category, paper.published].filter(Boolean).join(" · "),
                    }),
                    paper && paper.arxiv_id && T.jsx("p", {
                      className: "text-xs text-muted-foreground/50 mt-1",
                      children: paper.arxiv_id,
                    }),
                    paper && Array.isArray(paper.keywords) && paper.keywords.length > 0 && T.jsxs("div", {
                      className: "flex flex-wrap gap-2 mt-4",
                      children: paper.keywords.map((k, i) => T.jsx("span", {
                        className: "text-xs bg-cream-100 border border-cream-200 text-muted-foreground px-3 py-1 rounded-full",
                        children: k,
                      }, i)),
                    }),
                    paper && paper.abstract_zh && T.jsxs("div", {
                      className: "mt-4",
                      children: [
                        T.jsx("h4", { className: "text-sm font-semibold text-foreground", children: "摘要" }),
                        T.jsx("p", { className: "text-sm text-muted-foreground mt-2 leading-relaxed", children: paper.abstract_zh }),
                      ],
                    }),
                    paper && paper.abstract && paper.abstract_zh && paper.abstract !== paper.abstract_zh && T.jsxs("div", {
                      className: "mt-4",
                      children: [
                        T.jsx("h4", { className: "text-sm font-semibold text-foreground", children: "Abstract" }),
                        T.jsx("p", { className: "text-sm text-muted-foreground mt-2 leading-relaxed", children: paper.abstract }),
                      ],
                    }),
                    paper && paper.link && T.jsx("div", {
                      className: "mt-4",
                      children: T.jsx("a", {
                        href: paper.link,
                        target: "_blank",
                        rel: "noopener noreferrer",
                        className: "text-sm text-sunset-500 hover:text-sunset-600 font-medium",
                        children: "查看 arXiv 原文 →",
                      }),
                    }),
                  ],
                }),
              }),
              T.jsxs("div", {
                className: "flex-1 flex flex-col min-w-0",
                children: [
                  T.jsx(EA, { messages: messages, streamingContent: streaming }),
                  T.jsx(wA, { onSend: send, loading: loading }),
                ],
              }),
            ],
          }),
        ],
      }),
    ],
  });
}
function SA() {
  return T.jsxs(qE, {
    children: [
      T.jsx(qo, { path: "/login", element: T.jsx(uw, {}) }),
      T.jsx(qo, { path: "/", element: T.jsx(kA, {}) }),
      T.jsx(qo, { path: "/work", element: T.jsx(WkWorkPage, {}) }),
      T.jsx(qo, { path: "/digest", element: T.jsx(WkDigestPage, {}) }),
      T.jsx(qo, { path: "/papers", element: T.jsx(PpList, {}) }),
      T.jsx(qo, { path: "/papers/:id", element: T.jsx(PpChat, {}) }),
      T.jsx(qo, { path: "*", element: T.jsx(KE, { to: "/", replace: !0 }) }),
    ],
  });
}
Va.createRoot(document.getElementById("root")).render(
  T.jsx(wp.StrictMode, { children: T.jsx(ZE, { children: T.jsx(SA, {}) }) }),
);
